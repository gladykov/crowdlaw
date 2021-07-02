import PySimpleGUI as sg

from src.controller.common import BaseCtrl
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

    def set_new_branch(self):
        if self.model.branch_name is None:
            branch_name = self.model.get_new_branch_name()
            if branch_name in [None, "Cancel", ""]:
                exit()
            self.model.set_working_branch(branch_name)

            return True

        return False

    def event_handler(self, window, event, values):
        if self.ignore_event:
            self.ignore_event = not self.ignore_event
            return window

        if event == "doctree":
            self.ignore_event = self.model.select_document(window, values)
            return window

        if event == "add_file":
            new_file_result = self.model.add_document(values)
            if isinstance(new_file_result, list):
                warning_popup(new_file_result)
            elif new_file_result is True:
                new_window = self.get_window(
                    "title titel be a variable", window.CurrentLocation()
                )
                window.close()
                self.model.select_current_file(new_window)
                return new_window

        if event == "remove_file":
            reply = popup_yes_no_cancel(
                _("Confirm file deletion"),
                [_(f"Are you sure you want to remove file {values['doctree'][0]}")],
            )

            if reply == "yes":
                self.model.remove_document(values)
                new_window = self.get_window(
                    "title titel be a variable", window.CurrentLocation()
                )
                window.close()
                return new_window
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
                # TODO: Do not change branch in branch selector
                return window

            if self.model.set_working_branch(values["branch_selector"]):
                new_window = self.get_window(
                    "title titel be a variable", window.CurrentLocation()
                )
                window.close()
                return new_window

        if event in [_("Close"), sg.WIN_CLOSED]:
            window.close()
            return None

        return window
