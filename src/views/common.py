import PySimpleGUI as sg


def warning_popup(issues):
    layout = [
        [sg.Text(_("Found some issues, please correct them:"))],
    ]

    for issue in issues:
        layout.append([sg.Text(issue)])

    layout.append([sg.CloseButton(_("OK"))])
    window = sg.Window(_("Warning"), layout, finalize=True)
    while True:
        event, value = window.read()
        if event in [_("Close"), sg.WIN_CLOSED]:
            window.close()
            break
