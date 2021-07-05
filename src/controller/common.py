import PySimpleGUI as sg


def redo(text):
    # https://github.com/PySimpleGUI/PySimpleGUI/issues/2836
    try:  # if nothing to redo will cause "_tkinter.TclError: nothing to redo"
        text.edit_redo()
    except:
        pass


class BaseCtrl:
    def enable_undo(self, window, key):
        # Enable undo in multiline field
        text = window[key].Widget
        # Enable the undo mechanism
        text.configure(undo=True)
        # Bind redo mechanism to key Ctrl-Shift-Z
        text.bind("<Control-Shift-Key-Z>", lambda event, text=text: redo(text))

    def draw_window(self, window_title, layout, location=(None, None), modal=False):
        window = sg.Window(
            window_title, [[layout]], finalize=True, location=location, modal=modal
        )
        for element in window.AllKeysDict.keys():
            if window.AllKeysDict[element].Type in [
                "multiline"
            ]:  # TODO: Add to input as well
                self.enable_undo(window, element)

        return window
