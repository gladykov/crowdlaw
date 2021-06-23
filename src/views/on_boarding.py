import PySimpleGUI as sg


class OnBoardingUI:

    def __init__(self, controller_props):
        self.props = controller_props
        sg.theme(self.props.theme)

    def select_project_intention(self):

        elements = [
            [sg.Text(_("Before you start writing Law, we need few answers."))],
            [sg.Text(_("What do you want to do?"), key='updme')],
            [
                sg.Radio(_("Create fresh empty project, which others can join?"), 'intention',
                         default=(self.props.new_existing == 'new'), key='new', enable_events=True),
                sg.Radio(_("Join existing project?"), 'intention', default=(self.props.new_existing == 'existing'),
                         key='existing', enable_events=True)
            ]
        ]

        if self.props.new_existing is not None:
            if self.props.new_existing == "new":
                project_input = [sg.Text(_("Provide new project name")), sg.InputText(
                    self.props.project_name, key='project_name'
                )]
            else:
                project_input = [sg.Text(_("Provide URL of existing project")), sg.InputText(self.props.project_url,
                                 key='project_url')]

            elements.append(project_input)

        elements.append([sg.Button(_("Next")), sg.CloseButton(_("Cancel"))])

        main_frame = sg.Frame(_("Welcome to Crowd Law app"), elements, font=("Helvetica", 25))

        return main_frame

    def git_details(self):
        horizontal_line = [sg.HorizontalSeparator()]

        elements = []

        select_git_provider = [
            [sg.Text(
                _("In order to work with this tool, you will need account on Git site. It will take you only a moment."))],
            [sg.Text(_("Select Git site")), sg.Combo(
                values=self.props.supported_git_providers, default_value=_(self.props.git_provider or _("gitlab")),
                size=(20, 1), k='git_provider', readonly=True, disabled=(self.props.new_existing == 'existing'),
                enable_events=True)]
        ]

        for i in select_git_provider:
            elements.append(i)

        elements.append(horizontal_line)

        username_token = [

            [sg.Text(_(
                f"Provide {self.props.git_provider or _('gitlab')} username"), key='username_label'),
                sg.InputText(self.props.username, key='username_input'), sg.Text(
                _("No account? Create new."), text_color='blue', enable_events=True,
                key='create_account', font='Helvetica 10 underline')
            ],
            [sg.Text(
                _(f"Provide {self.props.git_provider or _('gitlab')} token"), key='token_label'),
                sg.InputText(self.props.token, key='token_input'), sg.Text(
                _("Obtain token"), text_color='blue', enable_events=True,
                key='obtain_token', font='Helvetica 10 underline')
            ],
            [sg.Text(
                _(f"Provide token name"), key='token_name_label'),
                sg.InputText(self.props.token, key='token_name_input')
            ],
        ]

        for element in username_token:
            elements.append(element)
        elements.append(
            [sg.Button(_("Back")), sg.CloseButton(_("Cancel")), sg.Button(_("Start!"))]
        )

        main_frame = sg.Frame(_("Git details"), elements, font=("Helvetica", 25))

        return main_frame
