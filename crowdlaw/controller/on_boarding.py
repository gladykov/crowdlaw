"""Controller for on boarding - collect all Git and project details"""
import os

import PySimpleGUI as sg

from crowdlaw.controller.common import BaseCtrl
from crowdlaw.model.on_boarding import OnBoardingModel
from crowdlaw.utils.utils import get_project_root
from crowdlaw.views.common import image_popup, warning_popup
from crowdlaw.views.on_boarding import OnBoardingUI


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
            window
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
        if self.common_event_handler(event):
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
                    _("Provide Git account details"), window.CurrentLocation()
                )
                if self.model.git_provider is not None and (
                    self.model.username in [None, ""]
                ):
                    self.model.fill_credentials(new_window, self.model.git_provider)
                window.close()
                return new_window

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

        if event == "demo_version":
            self.model.git_provider = "gitlab"
            self.model.new_existing = "existing"
            self.model.username = "gladykov"
            self.model.token = "glpat-QVFdF8iBW-LnysAxX_gH"
            self.model.token_name = "crowdlaw_read_only"
            self.model.project_url = (
                "https://gitlab.com/gladykov/example-project-for-crowd-law"
            )
            self.model.project_name = "example-project-for-crowd-law"

            initialization_result = self.model.initialize_project()
            if initialization_result is True:
                window.close()
                return True
            warning_popup(initialization_result)

        if event == "start":
            validation_result = self.model.validate_page_2(values)
            if validation_result is True:
                self.model.collect_page_2(values)
                initialization_result = self.model.initialize_project()
                if initialization_result is True:
                    window.close()
                    return True

                warning_popup(initialization_result)
            else:
                warning_popup(validation_result)

        if event in ["close", sg.WIN_CLOSED]:
            window.close()
            return None

        return window
