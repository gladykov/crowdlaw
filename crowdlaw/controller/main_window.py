"""Controller for application main window"""
from sys import exit

import pyperclip
import PySimpleGUI as sg
import yaml

from crowdlaw.controller.common import BaseCtrl
from crowdlaw.controller.on_boarding import OnBoardingCtrl
from crowdlaw.model.main_window import MainWindowModel
from crowdlaw.utils.utils import get_logger
from crowdlaw.views.common import (
    popup_yes_no_cancel,
    wait_cursor_disable,
    wait_cursor_enable,
    warning_popup,
)
from crowdlaw.views.main_window import MainWindowUI


logger = get_logger("root", log_level="debug")


class MainWindowCtrl(BaseCtrl):
    """Controller to manage main window"""

    def __init__(self):
        self.model = MainWindowModel()
        self.ignore_event = False  # Special flag for special cases

    def get_elements(self):
        """
        Collect all elements in layout to draw a window

        Returns:
            layout
        """
        return MainWindowUI(self.model).layout()

    def get_window(
        self, window_title, location=(None, None), size=(None, None), maximized=False
    ):
        """
        Draws window with given set of elements

        Args:
            window_title: str
            location: tuple
            size: tuple
            maximized: bool

        Returns:
            window
        """
        window = self.draw_window(
            window_title,
            self.get_elements(),
            location,
            False,
            size,
            True,
        )

        # Resize elements
        elements_to_expand_x = [
            "frame_stage",
            "center_column",
            "frame_document_editor",
            "document_editor",
        ]  # Order does matter

        for element in elements_to_expand_x:
            window[element].expand(expand_x=True)

        if maximized:
            window.maximize()

        return window

    def redraw_window(self, window):
        """
        Redraws window in a way, it will overlap previous window, and destroys old one.

        Args:
            window:

        Returns:
            window
        """
        new_window = self.get_window(
            self.model.app_title,
            window.CurrentLocation(),
            window.Size,
            maximized=self.maximized(window),
        )
        window.close()
        return new_window

    def select_current_project(self, window):
        """
        Select current project in UI

        Args:
            window: window
        Returns:
            None
        """
        window["project_selector"].update(self.model.project_name)

    def set_new_branch(self):
        """
        Set current working branch

        Returns:
            bool - True if branch was set properly, False if not
        """
        if self.model.branch_name is None:
            branch_name = self.model.get_new_branch_name()
            if branch_name in [None, "Cancel", ""]:
                exit()  # TODO: When user will close it ?
            self.model.set_working_branch(branch_name)

            return True

        return False

    def select_current_branch(self, window):
        """
        Select branch in UI

        Args:
            window:

        Returns:
            None
        """
        window["branch_selector"].update(self.model.branch_name)

    def update_token_info(self):
        """
        Update token info for all projects using same git provider
        Returns:
            None
        """
        on_boarding = OnBoardingCtrl()
        on_boarding.page = 2
        on_boarding.model.username = self.model.username
        on_boarding.model.token = self.model.token
        on_boarding.model.token_name = self.model.token_name
        on_boarding.model.git_provider = self.model.git_provider
        on_boarding_window = on_boarding.get_window(_("Update token info"), update=True)

        while True:
            update_token_event, update_token_values = on_boarding_window.read()
            on_boarding_window = on_boarding.event_handler(
                on_boarding_window, update_token_event, update_token_values
            )

            if update_token_event == "update":
                self.model.update_token_info(update_token_values)
                self.model = MainWindowModel()
                if self.model.remote_api.authenticated:
                    on_boarding_window.close()
                    break

                on_boarding_window["token_error"].update(
                    _("Couldn't authenticate with current token info")
                )

            elif update_token_event in [_("Close"), sg.WIN_CLOSED]:
                return False

    @staticmethod
    def update_stage_info(window):
        """
        Creates window to edit stages, validate user input and collect it.

        Args:
            window:

        Returns:
            dict, None:  When successful dict of stages
        """
        while True:
            event, values = window.read()
            if event in ["cancel", sg.WINDOW_CLOSED]:
                window.close()
                return None

            if event == "add_stage":
                stage_numbers = [
                    int(x.split("_")[-1])
                    for x in values.keys()
                    if x.startswith("stage_name_")
                ]
                new_stage_number = sorted(stage_numbers, reverse=True)[0] + 1

                window.extend_layout(
                    window["stages_col"],
                    [
                        [
                            sg.Radio(
                                "", "current", k=f"stage_is_active_{new_stage_number}"
                            ),
                            sg.Input(
                                default_text="",
                                k=f"stage_name_{new_stage_number}",
                                size=(30, 10),
                            ),
                            sg.Button("-", k=f"remove_stage_{new_stage_number}"),
                        ]
                    ],
                )

            if event.startswith("remove_stage_"):
                stage_number = event.split("_")[-1]
                for element in [
                    "stage_is_active_",
                    "stage_name_",
                    "remove_stage_",
                ]:
                    window[element + stage_number].update(visible=False)

            if event in ["save", "all_done"]:
                validation_error = False
                window["error"].update("")
                stage_numbers = [
                    x.split("_")[-1]
                    for x in values.keys()
                    if x.startswith("stage_name_")
                ]
                visible_stages = [
                    x for x in stage_numbers if window["stage_name_" + x].visible
                ]
                visible_stages.sort()
                active_stage = [
                    x for x in visible_stages if values["stage_is_active_" + x]
                ]

                if not active_stage and event != "all_done":
                    validation_error = True
                    window["error"].update(
                        _("At least one stage should be marked as active")
                    )

                if not validation_error:
                    for visible_stage in visible_stages:
                        if values["stage_name_" + visible_stage] == "":
                            window["error"].update(_("Provide name for every stage"))
                            validation_error = True

                if not validation_error:
                    stages_dict = {}
                    status = "completed"
                    new_number = 1
                    active_stage = active_stage[0] if event != "all_done" else "x"

                    for visible_stage in visible_stages:
                        if visible_stage == active_stage:
                            status = "active"
                        stages_dict[new_number] = {}
                        stages_dict[new_number]["name"] = values[
                            "stage_name_" + visible_stage
                        ]
                        stages_dict[new_number]["status"] = status
                        if status == "active":
                            status = "future"
                        new_number = new_number + 1

                    window.close()
                    return stages_dict

    def event_handler(self, window, event, values):
        """
        Main handler of events for window loop

        Args:
            window:
            event: str
            values: dict

        Returns:
            window, after successful handling of event;
            None if window is about to be destroyed
        """
        if window["copied_info"]._visible:
            window["copied_info"].update(visible=False)
            window.refresh()

        if self.ignore_event:
            self.ignore_event = not self.ignore_event
            return window

        event = self.events_preprocessor(event)

        # Handle menu items. Redraw if needed
        if self.common_event_handler(event):
            if self.model.protect_unsaved_changes(values["document_editor"]) not in [
                "cancel",
                None,
            ]:
                window = self.redraw_window(window)
                self.model.select_current_file(window)
                return window

        if event == "click_change_project":
            reply = MainWindowUI.change_project_popup()
            if reply not in [None, "Cancel"]:
                event = reply

        if event == "update_token_info":
            reply = popup_yes_no_cancel(
                _("Are you sure you want to update token info?"),
                [
                    _("Updating token info, will update it for all projects"),
                    _("which use {git_provider}").format(
                        git_provider=self.model.git_provider
                    ),
                    _("Are you sure?"),
                ],
            )
            if reply == "yes":
                if self.update_token_info() is not False:
                    return self.redraw_window(window)

        if event == "project_selector":
            wait_cursor_enable(window)
            if not values["project_selector"] == self.model.project_name:
                if self.model.protect_unsaved_changes(values["document_editor"]) in [
                    "cancel",
                    None,
                ]:
                    self.select_current_project(window)
                    wait_cursor_disable(window)
                    return window

                self.model.save_working_set()
                self.model = self.model.switch_project(values["project_selector"])
                return self.redraw_window(window)

        if event == "add_new_project":
            if self.model.protect_unsaved_changes(values["document_editor"]) in [
                "cancel",
                None,
            ]:
                self.select_current_project(window)
                return window

            on_boarding = OnBoardingCtrl()
            on_boarding_window = on_boarding.get_window(
                _("Add new project"), modal=True
            )

            while True:
                on_boarding_event, on_boarding_values = on_boarding_window.read()
                logger.debug(str(on_boarding_event) + "|" + str(on_boarding_values))
                on_boarding_window = on_boarding.event_handler(
                    on_boarding_window, on_boarding_event, on_boarding_values
                )
                if on_boarding_window is None:
                    break
                if on_boarding_window is True:
                    self.model.save_working_set()
                    self.model = MainWindowModel()
                    self.set_new_branch()
                    return self.redraw_window(window)

        if event == "remove_project":
            reply = popup_yes_no_cancel(
                _("Are you sure you want to remove project?"),
                [
                    _(
                        "WARNING: This will remove all project files "
                        "from your local computer"
                    ),
                    _("associated with project {project_name}.").format(
                        project_name=self.model.project_name
                    ),
                    _("Copy will be left on the server"),
                    _("To remove server version go to {server_url}").format(
                        server_url=self.model.project_url
                    ),
                    _("Are you sure you want ro remove files from local computer?"),
                ],
            )

            if reply == "yes":
                wait_cursor_enable(window)
                self.model.remove_project()
                self.model = MainWindowModel()
                return self.redraw_window(window)

        if event == "doctree":
            self.ignore_event = self.model.select_document(window, values)
            return window

        if event == "add_file":
            new_file_result = self.model.add_document(values)
            if isinstance(new_file_result, list):
                warning_popup(new_file_result)
            elif new_file_result is True:
                new_window = self.redraw_window(window)
                self.model.select_current_file(new_window)
                return new_window

        if event == "remove_file":
            reply = popup_yes_no_cancel(
                _("Confirm file deletion"),
                [
                    _("Are you sure you want to remove file {file} ?").format(
                        file=values["doctree"][0]
                    )
                ],
            )

            if reply == "yes":
                self.model.remove_document(values)
                return self.redraw_window(window)
            return window

        if event == "save":
            if self.model.edited_file is not None:
                self.model.put_file_content(
                    self.model.edited_file, values["document_editor"]
                )
            return window

        if event == "branch_selector":
            if self.model.protect_unsaved_changes(values["document_editor"]) in [
                "cancel",
                None,
            ]:
                self.select_current_branch(window)
                return window

            wait_cursor_enable(window)
            self.model.save_working_set()
            self.model.set_working_branch(values["branch_selector"])
            return self.redraw_window(window)

        if event == "add_new_set":
            if self.model.protect_unsaved_changes(values["document_editor"]) in [
                "cancel",
                None,
            ]:
                self.select_current_branch(window)
                return window

            wait_cursor_enable(window)
            self.model.save_working_set()
            result = self.model.add_new_branch()
            if result is True:
                return self.redraw_window(window)

            wait_cursor_disable(window)

            return window

        if event == "remove_set":
            reply = popup_yes_no_cancel(
                _("Are you sure you want to remove current set?"),
                [
                    _("All changes made in this set will be lost locally."),
                    _("They will be still available on the server, if you sent them"),
                    _("Are you sure you want to remove current set locally?"),
                ],
            )
            if reply == "yes":
                wait_cursor_enable(window)
                self.model.remove_current_branch()
                return self.redraw_window(window)

            return window

        if event == "send_to_review":
            if self.model.protect_unsaved_changes(values["document_editor"]) not in [
                "cancel",
                None,
            ]:
                wait_cursor_enable(window)
                if self.model.send_to_review(window) is False:
                    wait_cursor_disable(window)
                    return window

                self.model.update_review_info()
                window = self.redraw_window(window)
                self.model.select_current_file(window)
                return window

        if event == "update_review":
            if self.model.protect_unsaved_changes(values["document_editor"]) not in [
                "cancel",
                None,
            ]:
                wait_cursor_enable(window)
                self.model.update_review(values)
                wait_cursor_disable(window)
                return window

        if event is not None and event.startswith("URL"):
            self.model.open_url_in_browser(event.split(" ")[1])
            return window

        if event == "click_add_contact_info":
            if not self.model.protect_unsaved_changes(values["document_editor"]) in [
                "cancel",
                None,
            ]:
                ci_event, ci_values = MainWindowUI(self.model).add_contact_info_popup()
                if ci_event not in [None, "Cancel"]:
                    # Either it was empty and now it will be filled
                    # or it was filled, and now it will be empty
                    # unless was empty and will stay empty
                    if ci_values["contact_info"] or (
                        self.model.contact_info not in ["", None]
                        and not ci_values["contact_info"]
                    ):
                        wait_cursor_enable(window)
                        self.model.save_working_set()
                        self.model.set_maintainer_file(
                            "contact", ci_values["contact_info"]
                        )
                        window["contact_info"].update(ci_values["contact_info"])
                        self.model.contact_info = ci_values["contact_info"]
                        wait_cursor_disable(window)

            return window

        if event == "click_edit_stage_info":
            if not self.model.protect_unsaved_changes(values["document_editor"]) in [
                "cancel",
                None,
            ]:
                stage_dict = self.update_stage_info(
                    MainWindowUI(self.model).edit_stage_info()
                )
                if stage_dict is not None:
                    wait_cursor_enable(window)
                    self.model.save_working_set()
                    self.model.set_maintainer_file("stages.yaml", yaml.dump(stage_dict))
                    self.model.stages = stage_dict
                    return self.redraw_window(window)

            return window

        if event == "click_share_url":
            pyperclip.copy(self.model.project_url)
            window["copied_info"].update(visible=True)
            window.refresh()
            return window

        if event in [_("Close"), sg.WINDOW_CLOSE_ATTEMPTED_EVENT]:
            if not self.model.protect_unsaved_changes(values["document_editor"]) in [
                "cancel",
                None,
            ]:
                window.close()
                return None

        return window
