import PySimpleGUI as sg

from src.controller.common import BaseCtrl
from src.controller.language import LanguageCtrl
from src.controller.on_boarding import OnBoardingCtrl
from src.model.main_window import MainWindowModel
from src.utils.supported_langs import get_language_name_by_shortcut
from src.views.common import (
    animated_waiting, change_language_selector, popup_yes_no_cancel, warning_popup
)
from src.views.main_window import MainWindowUI


class MainWindowCtrl(BaseCtrl):
    """Base controller to manage main window"""

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

    def get_window(self, window_title, location=(None, None)):
        """
        Draws window with given set of elements

        Args:
            window_title: str
            location: tuple

        Returns:
            window
        """
        return self.draw_window(window_title, self.get_elements(), location)

    def redraw_window(self, window):
        """
        Redraws window in a way, it will overlap previous window, and destroys old one.

        Args:
            window:

        Returns:
            window
        """
        new_window = self.get_window(
            "title titel be a variable", window.CurrentLocation()
        )
        window.close()
        return new_window

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
            print(update_token_event, "|", update_token_values)
            on_boarding_window = on_boarding.event_handler(
                on_boarding_window, update_token_event, update_token_values
            )

            if update_token_event == "update":
                self.model.update_token_info(update_token_values)
                self.model = MainWindowModel()
                if self.model.remote_api.authenticated:
                    on_boarding_window.close()
                    break
                else:
                    on_boarding_window["token_error"].update(
                        _("Couldn't authenticate with current token info")
                    )

    def event_handler(self, window, event, values):
        """
        Main handler of events for window loop

        Args:
            window:
            event: str
            values: dict

        Returns:
            window, after successful handling of event; None if window is about to be destroyed
        """
        if self.ignore_event:
            self.ignore_event = not self.ignore_event
            return window

        event = self.events_preprocessor(event)

        if event == "change_language":
            reply = change_language_selector(
                LanguageCtrl.supported_langs(),
                get_language_name_by_shortcut(self.model.config["lang"]),
            )
            if reply[0] == "switch_language":
                new_lang = reply[1]["language_selector"]
                print(new_lang)
                if (
                    get_language_name_by_shortcut(LanguageCtrl.get_app_lang())
                    != new_lang
                ):
                    print(
                        f"Old lang {get_language_name_by_shortcut(LanguageCtrl.get_app_lang())} does not match new one {new_lang}"
                    )

                LanguageCtrl.switch_app_lang(new_lang)
                return self.redraw_window(window)

        if event == "click_change_project":
            reply = MainWindowUI.change_project_popup()
            if reply not in [None, "Cancel"]:
                event = reply

        if event == "update_token_info":
            reply = popup_yes_no_cancel(
                _("Are you sure you want to update token info?"),
                [
                    _("Updating token info, will update it for all projects"),
                    _(f"Which use {self.model.git_provider}"),
                    _(f"Are you sure?"),
                ],
            )
            if reply == "yes":
                self.update_token_info()
                return self.redraw_window(window)

        if event == "project_selector":
            if not values["project_selector"] == self.model.project_name:
                animated_waiting()
                if self.model.protect_unsaved_changes(values["document_editor"]) in [
                    "cancel",
                    None,
                ]:
                    self.model.select_current_project(window)
                    return window

                self.model.save_working_set()
                self.model = self.model.switch_project(values["project_selector"])
                return self.redraw_window(window)

        if event == "add_new_project":
            if self.model.protect_unsaved_changes(values["document_editor"]) in [
                "cancel",
                None,
            ]:
                self.model.select_current_project(window)
                return window

            on_boarding = OnBoardingCtrl()
            on_boarding_window = on_boarding.get_window(_("On boarding"))

            while True:
                on_boarding_event, on_boarding_values = on_boarding_window.read()
                print(on_boarding_event, "|", on_boarding_values)
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
                        "WARNING: This will remove all your files from your local computer"
                    ),
                    _(f"associated with project {self.model.project_name}."),
                    _("Copy will be left on the server"),
                    _(f"To remove server version go to {self.model.project_url}"),
                    _("Are you sure you want ro remove files from local computer?"),
                ],
            )

            if reply == "yes":
                remove_project_result = self.model.remove_project()
                self.model = MainWindowModel()
                if remove_project_result is True:
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
                [_(f"Are you sure you want to remove file {values['doctree'][0]}")],
            )

            if reply == "yes":
                self.model.remove_document(values)
                return self.redraw_window(window)
            else:
                return window

        if event == "save":
            if self.model.edited_file is not None:
                self.model.put_file_content(
                    self.model.edited_file, values["document_editor"]
                )

        if event == "branch_selector":
            if self.model.protect_unsaved_changes(values["document_editor"]) in [
                "cancel",
                None,
            ]:
                self.model.select_current_branch(window)
                return window

            self.model.save_working_set()
            if self.model.set_working_branch(values["branch_selector"]):
                return self.redraw_window(window)

        if event == "add_new_set":
            if self.model.protect_unsaved_changes(values["document_editor"]) in [
                "cancel",
                None,
            ]:
                self.model.select_current_branch(window)
                return window

            self.model.save_working_set()
            result = self.model.add_new_branch()
            return self.redraw_window(window) if result is True else window

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
                self.model.remove_current_branch()
                return self.redraw_window(window)

        if event == "send_to_review":
            self.model.send_to_review(values)
            self.model.update_review_info()
            return self.redraw_window(window)

        if event == "update_review":
            self.model.update_review(values)

        if event is not None and event.startswith("URL"):
            self.model.open_url_in_browser(event.split(" ")[1])

        if event in [_("Close"), sg.WIN_CLOSED]:
            window.close()
            return None

        return window
