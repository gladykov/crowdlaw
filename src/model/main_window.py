import logging
import os

import PySimpleGUI as sg

from src.api.api import get_api
from src.git_adapter.git_adapter import GitAdapter
from src.model.base import Base
from src.utils.utils import (
    get_project_root,
    get_token_name_token,
    replace_string_between_subs,
    strip_string,
)
from src.views.common import file_icon, folder_icon, popup_yes_no_cancel


logger = logging.getLogger("root")


class MainWindowModel(Base):
    def __init__(self):
        self.app_title = "Crowd Law 1.0"
        self.edited_file = None
        self.new_existing = None
        self.project_url = None
        self.project_name = None
        self.git_provider = None
        self.username = None
        self.token = None
        self.token_name = None
        self.theme = "DarkTeal6"  # Move to some common CTRL
        self.supported_git_providers = list(self.git_providers().keys())
        self.editor_disabled = True
        self.editor_text = ""
        self.edited_file = None

        self.config = self.get_config()
        self.project_name = self.config["last_project"]
        logger.info(
            _("Trying to initialize controller for project {project_name}").format(
                project_name=self.project_name
            )
        )
        self.git_adapter = GitAdapter(
            os.path.join(get_project_root(), "projects", self.project_name),
            initialized=True,
        )

        repo_url = self.git_adapter.get_config('remote "origin"', "url")
        self.token_name, self.token = get_token_name_token(repo_url)
        self.projects = self.folder_list(os.path.join(get_project_root(), "projects"))
        self.branch_names = self.git_adapter.local_branches()
        self.branch_name = self.git_adapter.repo.active_branch.name

        # Special case in case of crash
        if self.branch_name == "master":
            if len(self.branch_names) == 1:
                self.branch_name = None
            else:
                self.branch_name = list(
                    filter(lambda x: x != "master", self.git_adapter.local_branches())
                )[0]
                self.git_adapter.checkout_existing_branch(self.branch_name)

        self.branch_name_readable = ""
        self.project_url = self.config["projects"][self.project_name]["project_url"]
        self.username = self.config["projects"][self.project_name]["username"]
        self.project_folder = self.config["projects"][self.project_name]["folder"]
        self.git_provider = self.config["projects"][self.project_name]["provider"]
        self.list_of_files = self.tree_data()

        RemoteAPI = get_api(self.git_provider, self.git_providers())
        self.remote_api = RemoteAPI(self.username, self.token)
        self.stages = self.get_stages(self.project_name)
        self.merge_request = None

        if self.remote_api.authenticated:
            self.remote_api.set_current_project(self.username, self.project_name)
            self.update_review_info()

    def update_review_info(self):
        merge_requests = self.remote_api.get_merge_requests(
            self.username, self.branch_name
        )
        self.merge_request = merge_requests[0].web_url if merge_requests else None

    def update_list_of_files(self):
        self.list_of_files = self.tree_data()

    @staticmethod
    def folder_list(path):
        return [
            item for item in os.listdir(path) if os.path.isdir(os.path.join(path, item))
        ]

    def tree_data(self):
        tree_data = sg.TreeData()

        def add_files_in_folder(parent, dir_name):
            files = os.listdir(dir_name)
            for f in files:
                fullname = os.path.join(dir_name, f)
                if os.path.isdir(fullname):  # If it's a folder, add folder and recurse
                    if not ".git" in fullname.split(os.sep):  # Ignore .git folders
                        tree_data.Insert(
                            parent, fullname, f, values=[], icon=folder_icon
                        )
                        add_files_in_folder(fullname, fullname)
                else:
                    tree_data.Insert(
                        parent,
                        fullname,
                        f,
                        values=[],
                        icon=file_icon,
                    )

        add_files_in_folder(
            "", os.path.join(get_project_root(), "projects", self.project_name)
        )

        return tree_data

    @staticmethod
    def key_to_id(tree, key):
        for k, v in tree.IdToKey.items():
            if v == key:
                return k
        return None

    def select_current_file(self, window):
        window["doctree"].TKTreeview.selection_set(
            self.key_to_id(window["doctree"], self.edited_file)
        )
        # This triggers one event which we need to mute
        return True

    def select_document(self, window, values):
        if not self.valid_file_to_open(values["doctree"]):
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
        if self.protect_unsaved_changes(values["document_editor"]) in [
            "cancel",
            None,
        ]:
            return False

        new_filename = sg.popup_get_text(
            _("Provide new file name with .txt extension"), _("New filename")
        )
        if new_filename is None:
            return False

        issues = self.validate_new_filename(new_filename)
        if issues:
            return issues
        else:
            new_file_path = os.path.join(
                get_project_root(), "projects", self.project_name, new_filename
            )
            self.create_file(new_file_path)
            self.update_list_of_files()
            self.edited_file = new_file_path
            self.editor_text = ""
            self.editor_disabled = False
            return True

    def remove_document(self, values):
        self.remove_file(values["doctree"][0])
        self.update_list_of_files()
        self.edited_file = None

    @staticmethod
    def valid_file_to_open(file_list):
        valid_files = [
            "txt",
            "md",
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
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        return content

    @staticmethod
    def put_file_content(file_path, content):
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content.strip())

    @staticmethod
    def create_file(file_path):
        with open(file_path, "w") as fp:
            pass

    @staticmethod
    def remove_file(file_path):
        os.remove(file_path)

    @staticmethod
    def validate_new_filename(possible_name):
        issues = []
        if len(possible_name) == 0:
            issues.append(_("Filename cannot be empty"))

        if not possible_name.endswith(".txt"):
            issues.append(_("Filename must end with .txt"))

        return issues

    def protect_unsaved_changes(self, text_editor_value):
        if self.edited_file is None:
            return False

        text_editor_value = text_editor_value.rstrip()  # Text editor adds extra line
        if self.get_file_content(self.edited_file).rstrip() != text_editor_value:
            reply = popup_yes_no_cancel(
                _("Warning: Unsaved changes"),
                [
                    _(
                        "You have unsaved changes. "
                        "Do you want to save them before loading new document?"
                    )
                ],
            )

            if reply == "yes":
                self.put_file_content(self.edited_file, text_editor_value)

            return reply

        return False

    def update_text_editor(self, window, values):
        self.editor_disabled = False
        self.edited_file = values["doctree"][0]
        self.editor_text = self.get_file_content(self.edited_file)
        window["document_editor"].update(self.editor_text)
        window["document_editor"].update(disabled=self.editor_disabled)
        window["document_editor"].update(background_color="white")

    def get_new_branch_name(self):
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

        if branch_name in self.remote_api.get_branches():
            sg.popup_ok(
                _("Working set with name {branch_name} already exists").format(
                    branch_name=branch_name
                )
            )
            branch_name = self.get_new_branch_name()

        return branch_name

    def set_working_branch(self, branch_name, from_master=True):
        self.branch_name = branch_name
        if self.branch_exists(self.branch_name):
            self.git_adapter.checkout_existing_branch(self.branch_name)
            logger.info("Branch exists. Switch only.")
        else:
            logger.info("Branch does not exists. Create new one.")
            if from_master:
                self.git_adapter.checkout_master()
                self.git_adapter.checkout_new_branch(self.branch_name)
                self.git_adapter.push()
                self.git_adapter.pull()
                self.branch_names = self.git_adapter.local_branches()

        self.update_list_of_files()
        self.editor_text = ""
        self.edited_file = None
        self.editor_disabled = True
        self.update_review_info()

        return True

    def add_new_branch(self):
        branch_name = self.get_new_branch_name()
        if branch_name in [None, "Cancel", ""]:
            return False

        self.set_working_branch(branch_name)
        return True

    def branch_exists(self, branch_name):
        return branch_name in self.git_adapter.local_branches()

    def select_current_branch(self, window):
        window["branch_selector"].update(self.branch_name)

    def remove_current_branch(self):
        self.git_adapter.checkout_existing_branch("master")
        self.git_adapter.remove_branch(self.branch_name)
        self.branch_names = self.git_adapter.local_branches()
        if self.branch_names:
            self.set_working_branch(self.branch_names[0])
        else:
            self.add_new_branch()

    def select_current_project(self, window):
        window["project_selector"].update(self.project_name)

    def switch_project(self, project_name):
        self.config["last_project"] = project_name
        self.set_config(self.config)
        return MainWindowModel()

    def remove_project(self):
        self.config["projects"].pop(self.project_name)
        projects = self.config["projects"].keys()
        if len(projects) == 0:
            self.config["last_project"] = None
        else:
            self.config["last_project"] = sorted(projects)[0]

        self.set_config(self.config)
        self.git_adapter.remove_repo()
        return True

    def update_token_info(self, values):
        auth_string = f"{values['token_name_input']}:{values['token_input']}"

        provider_projects = []

        for key, value in self.config["projects"].items():
            if value["provider"] == self.git_provider:
                provider_projects.append(key)

        if provider_projects:
            for provider_project in provider_projects:
                repo = GitAdapter(
                    os.path.join(get_project_root(), "projects", provider_project),
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
        return True

    def save_working_set(self):

        if self.git_adapter.changes_exist():
            self.git_adapter.add_all_untracked()
            self.git_adapter.commit("Saved working set")

    def send_to_review(self, values):
        self.protect_unsaved_changes(values["document_editor"])
        if self.git_adapter.changes_exist():
            self.git_adapter.add_all_untracked()
            self.git_adapter.commit("Saved working set")

        self.git_adapter.push()

        merge_request_title = sg.popup_get_text(
            _("Provide title for your proposed changes"),
            _("Provide title for your proposed changes"),
        )

        if merge_request_title is None:
            return None

        self.remote_api.create_merge_request(
            self.username,
            self.project_name,
            self.branch_name,
            "master",
            merge_request_title,
        )

    def update_review(self, values):
        self.protect_unsaved_changes(values["document_editor"])
        if self.git_adapter.changes_exist():
            self.git_adapter.add_all_untracked()
            self.git_adapter.commit("Saved working set")

        self.git_adapter.push()
