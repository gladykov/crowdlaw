import PySimpleGUI as sg

from src.controller.common import BaseCtrl
from src.model.on_boarding import OnBoardingModel
from src.views.common import warning_popup
from src.views.on_boarding import OnBoardingUI


class OnBoardingCtrl(BaseCtrl):
    def __init__(self):
        self.model = OnBoardingModel()
        self.page = 1

    def get_elements(self):
        if self.page == 1:
            return OnBoardingUI(self.model).select_project_intention()
        else:
            return OnBoardingUI(self.model).git_details()

    def get_window(self, window_title, location=(None, None), modal=False):
        return self.draw_window(window_title, self.get_elements(), location, modal)

    def event_handler(self, window, event, values):
        if event == "new":
            self.model.new_existing = event
            new_window = self.get_window("updated", window.CurrentLocation())
            window.close()
            return new_window
        if event == "existing":
            self.model.new_existing = event
            new_window = self.get_window("existing", window.CurrentLocation())
            window.close()
            return new_window

        if event == "next":
            validation_result = self.model.validate_page_1(values)
            if validation_result is True:
                self.model.collect_page_1(values)
                self.page = 2
                new_window = self.get_window(
                    "git details title", window.CurrentLocation()
                )
                window.close()
                return new_window
            else:
                warning_popup(validation_result)

        if event == "back":
            self.page = 1
            self.model.collect_page_2(values)
            new_window = self.get_window("git details title", window.CurrentLocation())
            window.close()
            return new_window

        if event == "git_provider":
            self.model.fill_credentials(window, values)

        if event == "create_account":
            self.model.open_create_git_account()

        if event == "obtain_token":
            self.model.open_obtain_token()

        if event == "start":
            validation_result = self.model.validate_page_2(values)
            if validation_result is True:
                self.model.collect_page_2(values)
                initialization_result = self.model.initialize_project()
                if initialization_result is True:
                    window.close()
                    return True
                else:
                    warning_popup(initialization_result)
            else:
                warning_popup(validation_result)

        if event in ["close", sg.WIN_CLOSED]:
            window.close()
            return None

        return window
