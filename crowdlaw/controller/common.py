"""Common controller methods"""
import PySimpleGUI as sg

from crowdlaw.controller.language import LanguageCtrl
from crowdlaw.model.common import BaseModel
from crowdlaw.utils.supported_langs import get_language_name_by_shortcut
from crowdlaw.views.common import about, change_language_selector


def redo(text):
    """
    https://github.com/PySimpleGUI/PySimpleGUI/issues/2836
    """
    text.edit_redo()


class BaseCtrl:
    """BaseModel controller for all other controllers"""

    @staticmethod
    def enable_undo(window, key):
        """
        Enable undo in multiline field

        Args:
            window:
            key: str

        Returns:
            None
        """

        text = window[key].Widget
        # Enable the undo mechanism
        text.configure(undo=True)
        # Bind redo mechanism to key Ctrl-Shift-Z
        text.bind("<Control-Shift-Key-Z>", lambda event, text=text: redo(text))

    @staticmethod
    def enable_link(element):
        """
        Adds color, underline and hand cursor over clickable text/images/elements

        Args:
            element: PySg element

        Returns:
            Element
        """
        element.set_cursor("hand2")
        if element.Type == "text":
            element.update(font="Helvetica 10 underline", text_color="#add8e6")

        return element

    def draw_window(
        self,
        window_title,
        layout,
        location=(None, None),
        modal=False,
        size=(None, None),
        enable_close_attempted_event=False,
    ):
        """
        Draws final window on the screen.

        Args:
            window_title: str
            layout: sg layout
            location: tuple
            modal: bool - if true, will act as modal and block underlying window
            size: tuple
            enable_close_attempted_event: bool; should we confirm closing it

        Returns:
            window
        """
        window = sg.Window(
            window_title,
            [[layout]],
            finalize=True,
            location=location,
            size=size,
            modal=modal,
            resizable=True,
            enable_close_attempted_event=enable_close_attempted_event,
        )

        for element in window.AllKeysDict.keys():
            if window.AllKeysDict[element].Type in [
                "multiline",
                # "input",
                # TODO: Add to input as well
            ]:
                self.enable_undo(window, element)

            if isinstance(element, str) and (
                element.startswith("click") or element.startswith("URL")
            ):
                self.enable_link(window.AllKeysDict[element])

        return window

    @staticmethod
    def events_preprocessor(event):
        """
        Menu events look like this: 'Label::key' . Extract key from events like that.

        Returns
            str: event
        """
        return event.split("::")[-1] if event is not None else event

    @staticmethod
    def about():
        """
        Show about modal and open link if clicked

        Returns:
            None
        """
        window = about()
        window["open_link"].set_cursor("hand2")

        while True:
            event, _value = window.read()
            if event == "open_link":
                BaseModel.open_url_in_browser("https://gitlab.com/gladykov/crowdlaw/")
            else:
                window.close()
                break

    def common_event_handler(self, event):
        """
        Handles menu item entries

        Args:
            event: str

        Returns:
            bool; True if window should be redrawn, False if not
        """
        if event == "about":
            self.about()
            return False

        if event == "change_language":

            reply = change_language_selector(
                LanguageCtrl.supported_langs(),
                get_language_name_by_shortcut(BaseModel.get_config()["lang"]),
            )
            if reply[0] == "switch_language":
                new_lang = reply[1]["language_selector"]
                LanguageCtrl.switch_app_lang(new_lang)
                return True

        return False

    @staticmethod
    def maximized(window):
        """
        Check if given window is maximized.
        If you encounter cross-platform issues check maximize and minimize methods of
        PySimpleGUI for more cross platform hints.

        Args:
            window:

        Returns:
            bool
        """
        return window.TKroot.state() == "zoomed"
