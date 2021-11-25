"""UI elements callable from multiple views"""
import os
from platform import platform
from sys import version as pyversion
from time import sleep
from tkinter import TclVersion, TkVersion

import PySimpleGUI as sg

from crowdlaw.model.common import BaseModel
from crowdlaw.utils.utils import get_project_root


FOLDER_ICON = b"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABnUlEQVQ4y8WSv2rUQRSFv7vZgJFFsQg2EkWb4AvEJ8hqKVilSmFn3iNvIAp21oIW9haihBRKiqwElMVsIJjNrprsOr/5dyzml3UhEQIWHhjmcpn7zblw4B9lJ8Xag9mlmQb3AJzX3tOX8Tngzg349q7t5xcfzpKGhOFHnjx+9qLTzW8wsmFTL2Gzk7Y2O/k9kCbtwUZbV+Zvo8Md3PALrjoiqsKSR9ljpAJpwOsNtlfXfRvoNU8Arr/NsVo0ry5z4dZN5hoGqEzYDChBOoKwS/vSq0XW3y5NAI/uN1cvLqzQur4MCpBGEEd1PQDfQ74HYR+LfeQOAOYAmgAmbly+dgfid5CHPIKqC74L8RDyGPIYy7+QQjFWa7ICsQ8SpB/IfcJSDVMAJUwJkYDMNOEPIBxA/gnuMyYPijXAI3lMse7FGnIKsIuqrxgRSeXOoYZUCI8pIKW/OHA7kD2YYcpAKgM5ABXk4qSsdJaDOMCsgTIYAlL5TQFTyUIZDmev0N/bnwqnylEBQS45UKnHx/lUlFvA3fo+jwR8ALb47/oNma38cuqiJ9AAAAAASUVORK5CYII="  # noqa
FILE_ICON = b"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABU0lEQVQ4y52TzStEURiHn/ecc6XG54JSdlMkNhYWsiILS0lsJaUsLW2Mv8CfIDtr2VtbY4GUEvmIZnKbZsY977Uwt2HcyW1+dTZvt6fn9557BGB+aaNQKBR2ifkbgWR+cX13ubO1svz++niVTA1ArDHDg91UahHFsMxbKWycYsjze4muTsP64vT43v7hSf/A0FgdjQPQWAmco68nB+T+SFSqNUQgcIbN1bn8Z3RwvL22MAvcu8TACFgrpMVZ4aUYcn77BMDkxGgemAGOHIBXxRjBWZMKoCPA2h6qEUSRR2MF6GxUUMUaIUgBCNTnAcm3H2G5YQfgvccYIXAtDH7FoKq/AaqKlbrBj2trFVXfBPAea4SOIIsBeN9kkCwxsNkAqRWy7+B7Z00G3xVc2wZeMSI4S7sVYkSk5Z/4PyBWROqvox3A28PN2cjUwinQC9QyckKALxj4kv2auK0xAAAAAElFTkSuQmCC"  # noqa
TITLE_FONT_SIZE = 17


def warning_popup(issues):
    """
    Display simple warning popup with OK

    Args:
        issues: list - list of strings to show

    Returns:
        None
    """
    sg.popup_ok(*issues, title=_("Found some issues, please correct them."))


def image_popup(popup_text, image_path):
    """
    Display popup with image and OK

    Args:
        popup_text: str - text to show below image
        image_path: str - image path to show in popup

    Returns:
        None
    """
    sg.popup_ok(popup_text, title=_("Help"), image=image_path)


def popup_yes_no_cancel(title, issues):
    """
    Show popup with Yes, No, Cancel options

    Args:
        title: str
        issues: list

    Returns:
        str, None
    """
    text = "\n".join(issues)
    return sg.Window(
        title,
        [
            [sg.Text(text)],
            [
                sg.Button(_("Yes"), k="yes"),
                sg.Button(_("No"), k="no"),
                sg.Button(_("Cancel"), k="cancel"),
            ],
        ],
        modal=True,
    ).read(close=True)[0]


def help_icon(tooltip_text):
    """
    Get help icon with tooltip text

    Args:
        tooltip_text: str

    Returns:
        sg.Image
    """
    tooltip_text = tooltip_text.replace(". ", ". \n")

    return sg.Image(
        os.path.join(
            get_project_root(),
            "resources",
            "icons",
            "question-circle-regular.png",
        ),
        tooltip=tooltip_text,
    )


def help_icon_clickable(element_key):
    """
    Get help icon which can be clicked.
    By adding "click" as key beginning, method "enable_link" will add cursor
    Args:
        element_key: str

    Returns:
        sg.Image
    """
    return sg.Image(
        os.path.join(
            get_project_root(),
            "resources",
            "icons",
            "question-circle-regular.png",
        ),
        enable_events=True,
        key="click_" + element_key,
    )


def change_language_selector(language_list, current_language):
    """
    Prepare selector to change the language

    Args:
        language_list: list
        current_language: str

    Returns:
        sg.Frame
    """
    frame = sg.Frame(
        _("Select app language"),
        [
            [
                sg.Combo(
                    language_list,
                    enable_events=False,
                    default_value=current_language,
                    k="language_selector",
                ),
                sg.Button(_("Switch language"), k="switch_language"),
                sg.Button(_("Cancel"), k="cancel"),
            ]
        ],
        font=("Helvetica", TITLE_FONT_SIZE),
    )
    return sg.Window(_("Change app language"), [[frame]], modal=True).read(close=True)


def menu_toolbar():
    """
    Menu toolbar

    Returns:
        sg.Menu
    """
    menu_def = [
        [
            _("&Settings"),
            [_("&Change language") + "::change_language"],
        ],
        [_("&Help"), [_("&About") + "::about"]],
    ]
    return sg.Menu(menu_def, key="-MENU BAR-")


def ok_popup(text):
    """
    Show simple popup with OK button and simple info

    Args:
        text: str

    Returns:
        tuple(str, dict)
    """
    return sg.Window(
        _("Info"),
        [
            [sg.Text(text)],
            [sg.Button(_("OK"))],
        ],
        modal=True,
    ).read(close=True)


def about():
    """
    Show simple popup with OK button and simple info

    Returns:
        Window
    """
    return sg.Window(
        _("Info"),
        [
            [sg.Text(f"Crowd Law: {BaseModel.get_version()}")],
            [sg.Text(f"PySimpleGUI: {sg.__version__}")],
            [sg.Text(f"Tk / Tcl: {TkVersion, TclVersion }")],
            [sg.Text(f"Python: {pyversion.split(' ')[0]}")],
            [sg.Text(f"Platform: {platform()}")],
            [
                sg.Text(
                    "https://gitlab.com/gladykov/crowdlaw/",
                    k="open_link",
                    font="Helvetica 10 underline",
                    text_color="#add8e6",
                    enable_events=True,
                )
            ],
            [sg.Text("gladykov gmail com")],
            [sg.Button(_("OK"), bind_return_key=True)],
        ],
        modal=True,
        finalize=True,
        element_justification="c",
    )


def wait_cursor_enable(window):
    """
    Enable wait cursor.

    Args:
        window:

    Returns:
        None
    """
    window.TKroot.config(cursor="watch")
    sleep(0.7)  # Otherwise cursor change will not work
    # Still often does not work ¯\_(ツ)_/¯
    window.TKroot.update()


def wait_cursor_disable(window):
    """
    Disable wait cursor.

    Args:
        window:

    Returns:
        None
    """
    window.TKroot.config(cursor="")
    window.TKroot.update()
