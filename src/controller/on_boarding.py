import os

import PySimpleGUI as sg

from src.controller.common import BaseCtrl
from src.controller.language import LanguageCtrl
from src.model.on_boarding import OnBoardingModel
from src.utils.supported_langs import get_language_name_by_shortcut
from src.utils.utils import get_project_root
from src.views.common import change_language_selector, image_popup, warning_popup
from src.views.on_boarding import OnBoardingUI


class OnBoardingCtrl(BaseCtrl):
    """Controller handling joining project or creating new one"""

    def __init__(self):
        self.model = OnBoardingModel()
        self.page = 1

    def get_elements(self, update):
        """
        Get all elements to draw a window
        Args:
            update: bool - if true, only performs update of token info in repos

        Returns:
            PySG frame
        """
        if self.page == 1:
            return OnBoardingUI(self.model).select_project_intention()
        else:
            return OnBoardingUI(self.model).git_details(update)

    def get_window(
        self, window_title, location=(None, None), modal=False, update=False
    ):
        """
        Draws window with given set of elements
        Args:
            window_title: str
            location: tuple
            modal: bool
            update: bool - True, if only used to update token info

        Returns:

        """
        return self.draw_window(
            window_title, self.get_elements(update), location, modal
        )

    def redraw_window(self, window):
        """
        Redraws window in a way, it will overlap previous window, and destroys old one.

        Args:
            window:

        Returns:
            window
        """
        new_window = self.get_window(_("On Boarding"), window.CurrentLocation())
        window.close()
        return new_window

    def event_handler(self, window, event, values):
        """
        Main event handler of events in window, for window loop

        Args:
            window:
            event: str
            values: dict

        Returns:
            window, None
        """
        event = self.events_preprocessor(event)

        if event == "change_language":
            reply = change_language_selector(
                LanguageCtrl.supported_langs(),
                get_language_name_by_shortcut(self.model.config["lang"]),
            )
            if reply[0] == "switch_language":
                new_lang = reply[1]["language_selector"]
                LanguageCtrl.switch_app_lang(new_lang)
                return self.redraw_window(window)

        if event == "new":
            self.model.new_existing = event
            return self.redraw_window(window)
        if event == "existing":
            self.model.new_existing = event
            return self.redraw_window(window)

        if event == "next":
            validation_result = self.model.validate_page_1(values)
            if validation_result is True:
                self.model.collect_page_1(values)
                self.page = 2
                new_window = self.get_window(
                    "git details title", window.CurrentLocation()
                )
                if self.model.git_provider is not None and (
                    self.model.username in [None, ""]
                ):
                    self.model.fill_credentials(new_window, self.model.git_provider)
                window.close()
                return new_window
            else:
                warning_popup(validation_result)

        if event == "back":
            self.page = 1
            self.model.collect_page_2(values)
            return self.redraw_window(window)

        if event == "git_provider":
            self.model.fill_credentials(window, values["git_provider"])

        if event == "click_create_account":
            self.model.open_create_git_account()

        if event == "click_obtain_token":
            self.model.open_obtain_token()

        if event == "click_show_gitlab_help":
            image_popup(
                _(
                    "Clicking 'Obtain token' will take you to the git page. "
                    "Fill fields as on picture"
                ),
                os.path.join(
                    get_project_root(), "resources", "images", "gitlab_pat.png"
                ),
            )

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
