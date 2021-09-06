import os

import PySimpleGUI as sg

from src.utils.utils import get_project_root


folder_icon = b"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABnUlEQVQ4y8WSv2rUQRSFv7vZgJFFsQg2EkWb4AvEJ8hqKVilSmFn3iNvIAp21oIW9haihBRKiqwElMVsIJjNrprsOr/5dyzml3UhEQIWHhjmcpn7zblw4B9lJ8Xag9mlmQb3AJzX3tOX8Tngzg349q7t5xcfzpKGhOFHnjx+9qLTzW8wsmFTL2Gzk7Y2O/k9kCbtwUZbV+Zvo8Md3PALrjoiqsKSR9ljpAJpwOsNtlfXfRvoNU8Arr/NsVo0ry5z4dZN5hoGqEzYDChBOoKwS/vSq0XW3y5NAI/uN1cvLqzQur4MCpBGEEd1PQDfQ74HYR+LfeQOAOYAmgAmbly+dgfid5CHPIKqC74L8RDyGPIYy7+QQjFWa7ICsQ8SpB/IfcJSDVMAJUwJkYDMNOEPIBxA/gnuMyYPijXAI3lMse7FGnIKsIuqrxgRSeXOoYZUCI8pIKW/OHA7kD2YYcpAKgM5ABXk4qSsdJaDOMCsgTIYAlL5TQFTyUIZDmev0N/bnwqnylEBQS45UKnHx/lUlFvA3fo+jwR8ALb47/oNma38cuqiJ9AAAAAASUVORK5CYII="
file_icon = b"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABU0lEQVQ4y52TzStEURiHn/ecc6XG54JSdlMkNhYWsiILS0lsJaUsLW2Mv8CfIDtr2VtbY4GUEvmIZnKbZsY977Uwt2HcyW1+dTZvt6fn9557BGB+aaNQKBR2ifkbgWR+cX13ubO1svz++niVTA1ArDHDg91UahHFsMxbKWycYsjze4muTsP64vT43v7hSf/A0FgdjQPQWAmco68nB+T+SFSqNUQgcIbN1bn8Z3RwvL22MAvcu8TACFgrpMVZ4aUYcn77BMDkxGgemAGOHIBXxRjBWZMKoCPA2h6qEUSRR2MF6GxUUMUaIUgBCNTnAcm3H2G5YQfgvccYIXAtDH7FoKq/AaqKlbrBj2trFVXfBPAea4SOIIsBeN9kkCwxsNkAqRWy7+B7Z00G3xVc2wZeMSI4S7sVYkSk5Z/4PyBWROqvox3A28PN2cjUwinQC9QyckKALxj4kv2auK0xAAAAAElFTkSuQmCC"


def warning_popup(issues):
    """
    Display simple warning popup with OK

    Args:
        issues: list - list of strings to show

    Returns:
        None
    """
    # Expand box so title can be visible always
    issues.insert(0, "___________________________________________________________")
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
    # Expand box so title can be visible always
    issues.insert(0, "___________________________________________________________")
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
