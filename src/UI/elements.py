import PySimpleGUI as sg

folder_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABnUlEQVQ4y8WSv2rUQRSFv7vZgJFFsQg2EkWb4AvEJ8hqKVilSmFn3iNvIAp21oIW9haihBRKiqwElMVsIJjNrprsOr/5dyzml3UhEQIWHhjmcpn7zblw4B9lJ8Xag9mlmQb3AJzX3tOX8Tngzg349q7t5xcfzpKGhOFHnjx+9qLTzW8wsmFTL2Gzk7Y2O/k9kCbtwUZbV+Zvo8Md3PALrjoiqsKSR9ljpAJpwOsNtlfXfRvoNU8Arr/NsVo0ry5z4dZN5hoGqEzYDChBOoKwS/vSq0XW3y5NAI/uN1cvLqzQur4MCpBGEEd1PQDfQ74HYR+LfeQOAOYAmgAmbly+dgfid5CHPIKqC74L8RDyGPIYy7+QQjFWa7ICsQ8SpB/IfcJSDVMAJUwJkYDMNOEPIBxA/gnuMyYPijXAI3lMse7FGnIKsIuqrxgRSeXOoYZUCI8pIKW/OHA7kD2YYcpAKgM5ABXk4qSsdJaDOMCsgTIYAlL5TQFTyUIZDmev0N/bnwqnylEBQS45UKnHx/lUlFvA3fo+jwR8ALb47/oNma38cuqiJ9AAAAAASUVORK5CYII='

theme_dict = {'BACKGROUND': '#2B475D',
                'TEXT': '#FFFFFF',
                'INPUT': '#F2EFE8',
                'TEXT_INPUT': '#000000',
                'SCROLL': '#F2EFE8',
                'BUTTON': ('#000000', '#C2D4D8'),
                'PROGRESS': ('#FFFFFF', '#C7D5E0'),
                'BORDER': 1, 'SLIDER_DEPTH': 1, 'PROGRESS_DEPTH': 1}

# sg.theme_add_new('Dashboard', theme_dict)     # if using 4.20.0.1+
sg.LOOK_AND_FEEL_TABLE['Dashboard'] = theme_dict
sg.theme('Dashboard')

BORDER_COLOR = '#C7D5E0'
DARK_HEADER_COLOR = '#1B2838'
BPAD_TOP = ((20, 20), (20, 10))
BPAD_LEFT = ((20, 10), (0, 10))
BPAD_LEFT_INSIDE = (0, 10)
BPAD_RIGHT = ((10, 20), (10, 20))


def redo(event, text):
    # https://github.com/PySimpleGUI/PySimpleGUI/issues/2836
    try:    # if nothing to redo will cause "_tkinter.TclError: nothing to redo"
        text.edit_redo()
    except:
        pass


class Elements:

    def __init__(self):
        sg.theme('Dashboard')

    def repo_info(self):
        return sg.Frame(_("Server info"), [
            [sg.Text('URL: https://myurl.com')],
            [sg.Text('User: myuser', key="user")],
        ], font=("Helvetica", 25)
        )

    def documents_list(self):
        treedata = sg.TreeData()
        treedata.Insert("", "fullname", "f", values=[], icon=folder_icon)
        return sg.Frame(_("Documents"), [
            [sg.Text('File and folder browser Test')],
            [sg.Tree(headings=['Size', ], data=treedata, num_rows=20, col0_width=40)]
        ])

    def stage(self):
        return sg.Frame('Current stage', [[sg.Text('Current stage')]])

    def text_editor(self):
        frame = sg.Frame('Editor', [[sg.Multiline(size=(60, 20), key="MLINE_KEY")]])
        return frame

    def enable_undo(self, window, key):
        text = window[key].Widget
        # Enable the undo mechanism
        text.configure(undo=True)
        # Bind redo mechanism to key Ctrl-Shift-Z
        text.bind('<Control-Shift-Key-Z>', lambda event, text=text: redo(event, text))

    def layout(self):

        left_col = sg.Column([
            [self.repo_info()],
            [sg.HorizontalSeparator()],
            [self.documents_list()],
        ])

        center_col = sg.Column([
            [self.stage()],
            [sg.HorizontalSeparator()],
            [self.text_editor()],
            [sg.Button("Download")]
        ])

        layout = [
            [left_col, sg.VerticalSeparator(), center_col],
        ]

        window = sg.Window('Code Law 1.0', layout, background_color=BORDER_COLOR, finalize=True)
        self.enable_undo(window, 'MLINE_KEY')

        # Main window loop
        while True:
            event, values = window.read()

            window['user'].update('blabla')
            window.refresh()

            if event in ["Close", sg.WIN_CLOSED]:
                window.close()
                exit("App closed. Bye!")

    def am_i_selected_radio_button(self, key, event, default):
        if event is None:
            return default

    def on_boarding(self):

        def initial_elements(selected):
            return [
                [sg.Text(_("Before you start writing Law, we need few answers."))],
                [sg.Text(_("What do you want to do?", key='updme'))],
                [
                    sg.Radio(_("Create fresh empty project, which others can join?"), 'intention', default=True,
                             key='fresh', enable_events=True),
                    sg.Radio(_("Join existing project?"), 'intention', default=False, key='existing', enable_events=True)
                ]
            ]

        url_input = [sg.Text(_("Provide URL of existing project")), sg.InputText()]
        project_name_input = [sg.Text(_("Provide new project name")), sg.InputText()]
        next_cancel_buttons = [sg.Button("Next"), sg.CloseButton("Cancel")]
        select_git_provider = [
            [sg.Text(_("In order to work with this tool, you will need account on Git site. It will take you only a moment."))],
            [sg.Text(_("Select Git site"))],
            [sg.Combo(values=[_("gitlab")], default_value=_("gitlab"), size=(20, 1), k='git_provider',  readonly=True)]
        ]

        my_list = []

        for i in initial_elements(None):
            my_list.append(i)

        my_list.append(url_input)
        my_list.append(project_name_input)
        my_list.append([sg.HorizontalSeparator()])

        for i in select_git_provider:
            my_list.append(i)

        my_list.append(next_cancel_buttons)

        main_frame = sg.Frame(_("Welcome to Crowd Law app"), my_list



            # [sg.Text(_("Provide URL of existing project")), sg.InputText()],
            # ,
            #
            # [sg.Text(_("In order to work with this tool, you will need account on Git site. It will take you only a moment."))],
            # [sg.Text(_("Select Git site"))],
            # [sg.Combo(values=[_("gitlab")],
            #           default_value=_("gitlab"),
            #           size=(20, 1), k='git_provider',  readonly=True)
            # ]
            # ,
            # [sg.Button("Next"), sg.CloseButton("Cancel")]

        , font=("Helvetica", 25)
                        )

        window = sg.Window('Code Law 1.0', [[main_frame]], background_color=BORDER_COLOR, finalize=True)

        return window
