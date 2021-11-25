"""Module with model methods used by main window"""
import logging
import os

import PySimpleGUI as sg
import yaml

from crowdlaw.api.api import get_api
from crowdlaw.git_adapter.git_adapter import GitAdapter
from crowdlaw.model.common import BaseModel
from crowdlaw.utils.utils import (
    get_projects_path,
    get_token_name_token,
    replace_string_between_subs,
    strip_string,
    super_init,
    urljoin,
)
from crowdlaw.views.common import FILE_ICON, FOLDER_ICON, popup_yes_no_cancel


logger = logging.getLogger("root")


class MainWindowModel(BaseModel):
    """Main Window Model Class"""

    @super_init
    def __init__(self):
        self.app_title = f"Crowd Law {self.get_version()}"
        self.new_existing = None
        self.project_url = None
        self.project_name = None
        self.git_provider = None
        self.username = None
        self.token = None
        self.token_name = None
        self.supported_git_providers = list(self.git_providers().keys())
        self.editor_disabled = True
        self.editor_text = ""
        self.edited_file = None

        self.config = self.get_config()
        self.project_name = self.config["last_project"]
        self.demo_version = "example-project-for-crowd-law" == self.project_name
        logger.info(f"Trying to initialize controller for project {self.project_name}")
        self.git_adapter = GitAdapter(
            self.config["projects"][self.project_name]["folder"],
            initialized=True,
        )

        repo_url = self.git_adapter.get_config('remote "origin"', "url")
        self.token_name, self.token = get_token_name_token(repo_url)
        self.projects = list(self.config["projects"].keys())
        if len(self.projects) != len(self.folder_list(get_projects_path())):
            logger.warning(
                "List of projects in config does not match list of project folders"
            )
        self.branch_names = self.git_adapter.local_branches()
        self.branch_name = self.git_adapter.repo.active_branch.name

        # Special case in case of crash
        if self.branch_name == "master":
            if not self.branch_names:  # When only master, it will be empty list
                self.branch_name = None
            else:
                self.branch_name = self.branch_names[0]
                self.git_adapter.checkout_existing_branch(self.branch_name)

        self.project_url = self.config["projects"][self.project_name]["project_url"]
        self.username = self.config["projects"][self.project_name]["username"]
        self.is_owner = self.config["projects"][self.project_name]["is_owner"]
        self.project_folder = self.config["projects"][self.project_name]["folder"]
        self.git_provider = self.config["projects"][self.project_name]["provider"]
        self.list_of_files = self.tree_data()

        RemoteAPI = get_api(self.git_provider, self.git_providers())
        self.remote_api = RemoteAPI(self.username, self.token)
        self.merge_request = None
        self.contact_info = None
        self.stages = None

        if self.remote_api.authenticated:
            self.remote_api.set_current_project(self.username, self.project_name)
            self.update_review_info()

        self.contact_info = self.get_maintainer_file("contact")
        self.stages = self.get_stages()

    def set_maintainer_file(self, filename, file):
        """Write directly to root of repo on master branch

        Args:
            filename: str
            file: str - contents of file

        Returns:
            None
        """
        self.git_adapter.checkout_master()
        self.git_adapter.pull()
        with open(os.path.join(self.project_folder, filename), "w", newline="\n") as f:
            f.write(file)

        if not self.git_adapter.changes_exist():
            self.git_adapter.checkout_existing_branch(self.branch_name)
            return

        self.git_adapter.add_all_untracked()
        self.git_adapter.commit(
            f"Pushing maintainer file {filename} directly to master branch"
        )
        self.git_adapter.push()
        self.git_adapter.checkout_existing_branch(self.branch_name)

    def get_maintainer_file(self, filename):
        """
        Maintainer files, are special files, with latest info,
        which we try to fetch from master (not from forked, but from original).
        If not available, try local version.

        Args:
            filename: str

        Returns:
            str, None
        """
        if self.remote_api.authenticated:
            file = self.get_file_from_master(filename)
            if file is not None:
                return file

        return self.get_file_content(os.path.join(self.project_folder, filename))

    def get_stages(self):
        """
        Stages are our definition of current stage of the collaboration

        Returns:
            dict, None
        """
        file = self.get_maintainer_file("stages.yaml")
        if file is not None:
            stages = yaml.safe_load(file)
            return stages

        return None

    def get_file_from_master(self, filename):
        """Grab latest version of file from master, from root of repo,
        of original (not forked) repo

        Args:
            filename: str

        Returns:
            str, None
        """
        git_provider_dict = self.git_providers()[self.git_provider]

        project = self.remote_api.get_base_project_info(
            self.username, self.project_name
        )

        url = urljoin(
            [
                git_provider_dict["base_url"],
                project["username"],
                project["path"],
                git_provider_dict["get_raw_file_from_master"],
                "master",
                filename,
            ],
        )
        return self.get_file_from_url(url)

    def update_review_info(self):
        """
        Get info about merge request from API and update model"""
        merge_requests = self.remote_api.get_merge_requests(
            self.username, self.branch_name
        )
        self.merge_request = merge_requests[0].web_url if merge_requests else None

    def update_list_of_files(self):
        """
        Setup list of files
        """
        self.list_of_files = self.tree_data()

    @staticmethod
    def folder_list(path):
        """
        Collect all folders from given path

        Args:
            path: str

        Returns:
            list
        """
        return [
            item for item in os.listdir(path) if os.path.isdir(os.path.join(path, item))
        ]

    def tree_data(self):
        """
        Collect all files in folder

        Returns:
            sg.TreeData
        """
        tree_data = sg.TreeData()

        def add_files_in_folder(parent, dir_name):
            """

            Args:
                parent: str
                dir_name: str

            Returns:
                TreeData()
            """
            files = os.listdir(dir_name)
            for file in files:
                fullname = os.path.join(dir_name, file)
                if os.path.isdir(fullname):  # If it's a folder, add folder and recurse
                    if ".git" not in fullname.split(os.sep):  # Ignore .git folders
                        tree_data.Insert(
                            parent, fullname, file, values=[], icon=FOLDER_ICON
                        )
                        add_files_in_folder(fullname, fullname)
                else:
                    if ".txt" in file:
                        tree_data.Insert(
                            parent,
                            fullname,
                            file,
                            values=[],
                            icon=FILE_ICON,
                        )

        add_files_in_folder("", os.path.join(get_projects_path(), self.project_name))

        return tree_data

    @staticmethod
    def key_to_id(tree, key):
        """
        Helper to identify items on list of sg.Tree

        Args:
            tree: sg.TreeData
            key: str

        Returns:
            str, None
        """
        for k, v in tree.IdToKey.items():
            if v == key:
                return k
        return None

    def select_current_file(self, window):
        """
        Select item on sg.Tree element

        Args:
            window:

        Returns:
            bool
        """
        if self.edited_file is None:
            return

        window["doctree"].TKTreeview.selection_set(
            self.key_to_id(window["doctree"], self.edited_file)
        )
        # This triggers one event which we need to mute
        return True

    def select_document(self, window, values):
        """
        Select item in sg.Tree

        Args:
            window:
            values: dict

        Returns:
            bool
        """
        if not self.valid_file_to_open(values["doctree"]):
            return False

        if values["doctree"][0] == self.edited_file:  # Clicked already opened document
            return False

        if self.edited_file is None:
            self.update_text_editor(window, values)
        else:
            reply = self.protect_unsaved_changes(values["document_editor"])
            if reply is False or reply in ["yes", "no"]:
                self.update_text_editor(window, values)
            else:
                return self.select_current_file(window)

        return False

    def add_document(self, values):
        """
        Create new document routine.

        Args:
            values: dict

        Returns:
            bool
        """
        if self.protect_unsaved_changes(values["document_editor"]) in [
            "cancel",
            None,
        ]:
            return False

        new_filename = sg.popup_get_text(_("Provide new file name"), _("New filename"))
        if new_filename is None:
            return False

        issues = self.validate_new_filename(new_filename)
        if issues:
            return issues

        if not new_filename.endswith(".txt"):
            new_filename = new_filename + ".txt"

        new_file_path = os.path.join(
            get_projects_path(), self.project_name, new_filename
        )
        self.create_file(new_file_path)
        self.update_list_of_files()
        self.edited_file = new_file_path
        self.editor_text = ""
        self.editor_disabled = False
        return True

    def remove_document(self, values):
        """
        Remove document routine

        Args:
            values: dicts

        Returns:
             None
        """
        self.remove_file(values["doctree"][0])
        self.update_list_of_files()
        self.edited_file = None
        self.editor_text = ""
        self.editor_disabled = True

    @staticmethod
    def valid_file_to_open(file_list):
        """
        Check if this type of file should be handled by editor

        Args:
            file_list: list of files from values dict

        Returns:
            bool
        """
        valid_files = [
            "txt",
        ]

        if len(file_list) != 1:
            return False

        if not os.path.isfile(file_list[0]):
            return False

        for extension in valid_files:
            if file_list[0].lower().endswith("." + extension):
                return True

        return False

    @staticmethod
    def get_file_content(file_path):
        """
        Load file into memory

        Args:
            file_path: str

        Returns:
            str, None
        """
        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                return content

        return None

    @staticmethod
    def put_file_content(file_path, content):
        """
        Save file on disk
        Args:
            file_path: str
            content: str

        Returns:
            None
        """
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content.strip())

    @staticmethod
    def create_file(file_path):
        """
        Create file on disk without content.

        Args:
            file_path: str

        Returns:
            None
        """
        with open(file_path, "w"):
            pass

    @staticmethod
    def remove_file(file_path):
        """
        Remove file from disk.

        Args:
            file_path: str

        Returns:
            None
        """
        os.remove(file_path)

    @staticmethod
    def validate_new_filename(possible_name):
        """
        Validate new file name.

        Args:
            possible_name: str

        Returns:
            list
        """
        issues = []
        if len(possible_name) == 0:
            issues.append(_("Filename cannot be empty"))

        return issues

    def protect_unsaved_changes(self, text_editor_value):
        """
        Trying to save file if there are unsaved changes.

        Args:
            text_editor_value: str;

        Returns:
            bool, str
        """
        if self.edited_file is None:
            return False

        text_editor_value = text_editor_value.rstrip()  # Text editor adds extra line
        if self.get_file_content(self.edited_file).rstrip() != text_editor_value:
            reply = popup_yes_no_cancel(
                _("Warning: Unsaved changes"),
                [
                    _(
                        "You have unsaved changes in editor. "
                        "Do you want to save them before proceeding?"
                    )
                ],
            )

            if reply == "yes":
                self.put_file_content(self.edited_file, text_editor_value)
                self.editor_text = text_editor_value

            return reply

        return False

    def update_text_editor(self, window, values):
        """
        Enable and update text inside editor.

        Args:
            window: window
            values: dict

        Returns:
            None
        """
        self.editor_disabled = False
        self.edited_file = values["doctree"][0]
        self.editor_text = self.get_file_content(self.edited_file)
        window["document_editor"].update(self.editor_text)
        window["document_editor"].Widget.edit_reset()  # Clear undo history stack
        window["document_editor"].update(disabled=self.editor_disabled)
        window["document_editor"].update(background_color="white")

    def get_new_branch_name(self):
        """
        Get new branch (working set) from user.

        Returns:
            str, None
        """
        branch_name = sg.popup_get_text(
            _(
                "All your changes to the articles,\n"
                "will be treated together as one set\n"
                "Please, give a short name to a new set of changes"
            ),
            _("Provide name for your set of changes"),
        )

        if branch_name is None:
            return None

        if not branch_name:
            branch_name = self.get_new_branch_name()

        branch_name = strip_string(branch_name)

        if (
            branch_name in self.remote_api.get_branches()
            or branch_name in self.branch_names
        ):
            sg.popup_ok(
                _("Working set with name {branch_name} already exists").format(
                    branch_name=branch_name
                )
            )
            branch_name = self.get_new_branch_name()

        return branch_name

    def set_working_branch(self, branch_name):
        """
        Set current branch (working set). If needed create new branch.

        Args:
            branch_name: str

        Returns:
            None
        """
        if self.branch_exists_locally(branch_name):
            self.git_adapter.checkout_existing_branch(branch_name)
            logger.info(f"Branch {branch_name} exists. Switch only.")
        else:
            logger.info(f"Branch {branch_name} does not exists. Create new one.")
            self.git_adapter.checkout_master()
            self.git_adapter.pull()
            self.git_adapter.checkout_new_branch(branch_name)
            self.branch_names = self.git_adapter.local_branches()

        self.branch_name = branch_name
        self.update_list_of_files()
        self.editor_text = ""
        self.edited_file = None
        self.editor_disabled = True
        self.update_review_info()

    def add_new_branch(self):
        """
        Add new branch. Will also create and checkout.

        Returns:
            bool
        """
        branch_name = self.get_new_branch_name()
        if branch_name in [None, "Cancel", ""]:
            return False

        self.set_working_branch(branch_name)

        return True

    def branch_exists_locally(self, branch_name):
        """
        Check if branch exists locally.

        Args:
            branch_name: str

        Returns:
            bool
        """
        return branch_name in self.git_adapter.local_branches()

    def remove_current_branch(self):
        """
        Remove current branch from disk

        Returns:
            None
        """
        self.git_adapter.checkout_existing_branch("master")
        self.git_adapter.remove_branch(self.branch_name)
        self.branch_names = self.git_adapter.local_branches()
        if self.branch_names:
            self.set_working_branch(self.branch_names[0])
        else:
            added = False
            while added is not True:
                added = self.add_new_branch()

    def switch_project(self, project_name):
        """
        Switch project for the app.

        Args:
            project_name: str

        Returns:
            MainWindowModel
        """
        self.config["last_project"] = project_name
        self.set_config(self.config)
        return MainWindowModel()

    def remove_project(self):
        """
        Remove current project from disk

        Returns:
            None
        """
        self.config["projects"].pop(self.project_name)
        projects = self.config["projects"].keys()
        self.config["last_project"] = (
            None if len(projects) == 0 else sorted(projects)[0]
        )

        self.set_config(self.config)
        self.git_adapter.remove_repo()

    def update_token_info(self, values):
        """
        Update token info across all projects using same git provider.

        Args:
            values: dict

        Returns:
            None
        """
        auth_string = f"{values['token_name_input']}:{values['token_input']}"

        provider_projects = []

        for key, value in self.config["projects"].items():
            if value["provider"] == self.git_provider:
                provider_projects.append(key)

        if provider_projects:
            for provider_project in provider_projects:
                repo = GitAdapter(
                    os.path.join(get_projects_path(), provider_project),
                    initialized=True,
                )
                url = repo.get_config('remote "origin"', "url")
                new_url = replace_string_between_subs(url, "://", auth_string, "@")
                repo.set_config('remote "origin"', "url", new_url)

        self.config["git_providers"][self.git_provider]["token"] = values["token_input"]
        self.config["git_providers"][self.git_provider]["token_name"] = values[
            "token_name_input"
        ]
        self.set_config(self.config)

    def save_working_set(self):
        """
        Save working set (current branch) by adding all untrcked files and commiting
        them, without pushing.

        Returns:
            None
        """
        if self.git_adapter.changes_exist():
            self.git_adapter.add_all_untracked()
            self.git_adapter.commit("Saved working set")

    def send_to_review(self, window):
        """
        Send for code review
        Args:
            window: sg.Window

        Returns:
            None
        """
        if self.git_adapter.changes_exist():
            self.git_adapter.add_all_untracked()
            self.git_adapter.commit("Saved working set")

        merge_request_title = sg.popup_get_text(
            _("Provide title for your proposed changes"),
            _("Provide title for your proposed changes"),
        )

        if merge_request_title is None:
            return False

        if self.git_adapter.reset_identical_commits() is False:
            # No local commits to push
            window["review_info"].update(
                _("No changes to send. Edit some files first.")
            )
            return False

        self.git_adapter.commit(merge_request_title)
        self.git_adapter.push()

        self.remote_api.create_merge_request(
            self.username,
            self.project_name,
            self.branch_name,
            "master",
            merge_request_title,
        )

    def update_review(self, values):
        """
        Update existing merge request by pushing latest changes

        Args:
            values: dict

        Returns:
            None
        """
        if self.git_adapter.changes_exist():
            self.git_adapter.add_all_untracked()
            self.git_adapter.commit("Saved working set")

            self.git_adapter.reset_identical_commits()
            self.git_adapter.commit(_("Updates to review"))
            self.git_adapter.push()
