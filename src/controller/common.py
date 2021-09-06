import logging

import PySimpleGUI as sg


def redo(text):
    # https://github.com/PySimpleGUI/PySimpleGUI/issues/2836
    try:  # if nothing to redo will cause "_tkinter.TclError: nothing to redo"
        text.edit_redo()
    except:
        pass


class BaseCtrl:
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
            None
        """
        element.set_cursor("hand2")
        if element.Type == "text":
            element.update(font="Helvetica 10 underline", text_color="#add8e6")

    def draw_window(self, window_title, layout, location=(None, None), modal=False):
        """
        Draws final window on the screen.

        Args:
            window_title: str
            layout: sg layout
            location: tuple
            modal: bool - if true, will act as modal and block underlying window

        Returns:
            window
        """
        window = sg.Window(
            window_title,
            [[layout]],
            finalize=True,
            location=location,
            modal=modal,
            resizable=True,
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

        # window["stdout"].reroute_stdout_to_here()
        # window["stdout"].reroute_stderr_to_here()

        return window
