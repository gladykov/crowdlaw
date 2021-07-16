import PySimpleGUI as sg

from src.controller.common import BaseCtrl
from src.controller.on_boarding import OnBoardingCtrl
from src.model.main_window import MainWindowModel
from src.views.common import popup_yes_no_cancel, warning_popup
from src.views.main_window import MainWindowUI


class MainWindowCtrl(BaseCtrl):
    def __init__(self):
        self.model = MainWindowModel()
        self.ignore_event = False  # Special flag for special cases

    def get_elements(self):
        return MainWindowUI(self.model).layout()

    def get_window(self, window_title, location=(None, None)):
        return self.draw_window(window_title, self.get_elements(), location)

    def redraw_window(self, window):
        new_window = self.get_window(
            "title titel be a variable", window.CurrentLocation()
        )
        window.close()
        return new_window

    def set_new_branch(self):
        if self.model.branch_name is None:
            branch_name = self.model.get_new_branch_name()
            if branch_name in [None, "Cancel", ""]:
                exit()  # TODO: When user will close it ?
            self.model.set_working_branch(branch_name)

            return True

        return False

    def event_handler(self, window, event, values):
        if self.ignore_event:
            self.ignore_event = not self.ignore_event
            return window

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
                on_boarding = OnBoardingCtrl()
                on_boarding.page = 2
                on_boarding.model.username = self.model.username
                on_boarding.model.token = self.model.token
                on_boarding.model.token_name = self.model.token_name
                on_boarding_window = on_boarding.get_window(
                    _("Update token info"), update=True
                )

                update_token_event, update_token_values = on_boarding_window.read(
                    close=True
                )
                if update_token_event == "update":
                    self.model.update_token_info(update_token_values)
                    self.model = MainWindowModel()
                    return self.redraw_window(window)

        if event == "project_selector":
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
                    _(f"associated with project {self.project_name}."),
                    _("Copy will be left on the server"),
                    _(f"To remove server version go to {self.project_url}"),
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
            self.model.add_new_branch()
            return self.redraw_window(window)

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
