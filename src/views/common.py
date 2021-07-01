import PySimpleGUI as sg


def warning_popup(issues):
    # Expand box so title can be visible always
    issues.insert(0, "___________________________________________________________")
    sg.popup_ok(*issues, title=_("Found some issues, please correct them."))


def popup_yes_no_cancel(title, issues):
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
