import os.path
import webbrowser
from time import time

import PySimpleGUI as sg
import validators

from src.api.api import get_api
from src.controller.common import CommonCtrl, file_icon, folder_icon
from src.git_adapter.git_adapter import GitAdapter
from src.utils.utils import (
    PropertiesMainWindow, PropertiesOnboarding, get_config,
    get_git_providers, get_project_root, set_config, strip_string
)
from src.views.common import popup_yes_no_cancel, warning_popup
from src.views.main_window import MainWindowUI


class MainWindowCtrl(CommonCtrl):
    def __init__(self):
        self.props = PropertiesMainWindow()
        self.config = get_config()
        self.props.project_name = self.config["last_project"]
        self.props.branch_name = self.config.get("last_branch")
        self.props.project_url = self.config["projects"][self.props.project_name][
            "repo"
        ]["url"]
        self.props.username = self.config["projects"][self.props.project_name]["repo"][
            "user"
        ]
        self.props.list_of_files = self.get_treedata(
            os.path.join(get_project_root(), "projects", "monopipeline")
        )
        self.ignore_event = False  # Special flag for special cases
        self.git_adapter = GitAdapter(
            os.path.join(get_project_root(), "projects", "monopipeline"),
            initialized=True,
        )
        self.props.branch_names = self.git_adapter.local_branches()

    @staticmethod
    def key_to_id(tree, key):
        for k, v in tree.IdToKey.items():
            if v == key:
                print(f"Found {k} for {v}")
                return k
        return None

    @staticmethod
    def get_treedata(starting_path):
        treedata = sg.TreeData()

        def add_files_in_folder(parent, dirname):
            files = os.listdir(dirname)
            for f in files:
                fullname = os.path.join(dirname, f)
                if os.path.isdir(fullname):  # if it's a folder, add folder and recurse
                    treedata.Insert(parent, fullname, f, values=[], icon=folder_icon)
                    add_files_in_folder(fullname, fullname)
                else:
                    treedata.Insert(
                        parent,
                        fullname,
                        f,
                        values=[],
                        icon=file_icon,
                    )

        add_files_in_folder("", starting_path)

        return treedata

    def select_current_file(self, window):
        window["doctree"].TKTreeview.selection_set(
            self.key_to_id(window["doctree"], self.props.edited_file)
        )
        # This triggers one event which we need to mute
        self.ignore_event = True

    def get_elements(self):
        return MainWindowUI(self.props).layout()

    def get_window(self, window_title, location=(None, None)):
        return self.draw_window(window_title, self.get_elements(), location)

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
        with open(file_path, "r") as file:
            content = file.read()
        return content

    @staticmethod
    def put_file_content(file_path, content):
        with open(file_path, "w") as file:
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
        if self.props.edited_file is None:
            return False

        text_editor_value = text_editor_value.rstrip()  # Text editor adds extra line
        if self.get_file_content(self.props.edited_file).rstrip() != text_editor_value:
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
                self.put_file_content(self.props.edited_file, text_editor_value)

            return reply

        return False

    def update_text_editor(self, window, values):
        self.props.editor_disabled = False
        self.props.edited_file = values["doctree"][0]
        self.props.editor_text = self.get_file_content(self.props.edited_file)
        window["document_editor"].update(self.props.editor_text)
        window["document_editor"].update(disabled=self.props.editor_disabled)
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

        self.props.branch_name_readable = branch_name
        # Make sure branch name is unique
        # TODO: Make proper branch name validation
        return strip_string(branch_name) + "_" + str(time())[-3:]

    def set_working_branch(self, window, branch_name):
        self.props.branch_name = branch_name
        if self.branch_exists(self.props.branch_name):
            self.git_adapter.checkout_existing_branch(self.props.branch_name)
            print("branch exists")
        else:
            print("branch not exists")
            self.git_adapter.checkout_new_branch(self.props.branch_name)
            self.props.branch_names = self.git_adapter.local_branches()

        self.props.list_of_files = self.get_treedata(
            os.path.join(get_project_root(), "projects", "monopipeline")
        )
        new_window = self.get_window(
            "title titel be a variable", window.CurrentLocation()
        )
        window.close()
        return new_window

    def branch_exists(self, branch_name):
        return branch_name in self.git_adapter.local_branches()

    def event_handler(self, window, event, values):
        if self.ignore_event:
            self.ignore_event = not self.ignore_event
            return window

        if event == "doctree":
            if not self.valid_file_to_open(values["doctree"]):
                return window

            if self.props.edited_file is None:
                self.update_text_editor(window, values)
            else:
                reply = self.protect_unsaved_changes(values["document_editor"])
                if reply is False or reply in ["yes", "no"]:
                    self.update_text_editor(window, values)
                else:
                    self.select_current_file(window)

            return window

        if event == "add_file":
            if self.protect_unsaved_changes(values["document_editor"]) in [
                "cancel",
                None,
            ]:
                return window

            new_filename = sg.popup_get_text(
                _("Provide new file name with .txt extension"), _("New filename")
            )
            if new_filename is None:
                return window
            issues = self.validate_new_filename(new_filename)
            if issues:
                warning_popup(issues)
            else:
                new_file_path = os.path.join(
                    get_project_root(), "projects", "monopipeline", new_filename
                )
                self.create_file(new_file_path)
                self.props.list_of_files = self.get_treedata(
                    os.path.join(get_project_root(), "projects", "monopipeline")
                )
                self.props.edited_file = new_file_path
                self.props.editor_text = ""
                self.props.editor_disabled = False
                new_window = self.get_window(
                    "title titel be a variable", window.CurrentLocation()
                )
                window.close()
                self.select_current_file(new_window)
                return new_window

        if event == "remove_file":
            reply = popup_yes_no_cancel(
                _("Confirm file deletion"),
                [_(f"Are you sure you want to remove file {values['doctree'][0]}")],
            )

            if reply == "yes":
                self.remove_file(values["doctree"][0])
                self.props.list_of_files = self.get_treedata(
                    os.path.join(get_project_root(), "projects", "monopipeline")
                )
                self.props.edited_file = None
                new_window = self.get_window(
                    "title titel be a variable", window.CurrentLocation()
                )
                window.close()
                return new_window
            else:
                return window

        if event == "save":
            if self.props.edited_file is not None:
                self.put_file_content(self.props.edited_file, values["document_editor"])
                window["document_editor"].update(disabled=False)

        if event == "branch_selector":
            if self.protect_unsaved_changes(values["document_editor"]) in [
                "cancel",
                None,
            ]:
                # TODO: Do not change branch
                return window

            return self.set_working_branch(window, values["branch_selector"])

        if event in [_("Close"), sg.WIN_CLOSED]:
            window.close()
            return None

        return window
