"""UI elements shown during on boarding and editing Git details"""
import PySimpleGUI as sg

from crowdlaw.views.common import help_icon_clickable, menu_toolbar


class OnBoardingUI:
    """Add/Edit project, git details, token details"""

    def __init__(self, controller_props):
        self.props = controller_props
        sg.theme(self.props.theme)

    def select_project_intention(self):
        """
        Fresh / existing project; URL of existing project.

        Returns:
            Frame
        """
        elements = [
            [menu_toolbar()],
            [sg.Text(_("Before you start writing Law, we need few answers."))],
            [sg.Text(_("What do you want to do?"))],
            [
                sg.Radio(
                    _("Create fresh empty project, which others can join"),
                    "intention",
                    default=(self.props.new_existing == "new"),
                    k="new",
                    enable_events=True,
                ),
                sg.Radio(
                    _("Join existing project"),
                    "intention",
                    default=(self.props.new_existing == "existing"),
                    k="existing",
                    enable_events=True,
                ),
            ],
        ]

        if not self.props.config[
            "init"
        ]:  # Give possibility to see demo only on first launch
            elements.append(
                [
                    sg.Button(_("Launch demo version"), k="demo_version"),
                    sg.Text(
                        _("Join demo project to preview application"),
                        text_color="grey",
                        justification="right",
                    ),
                ]
            )

        if self.props.new_existing is not None:
            if self.props.new_existing == "new":
                project_input = [
                    sg.Text(_("Provide new project name")),
                    sg.InputText(self.props.project_name, k="project_name"),
                ]
            else:
                project_input = [
                    sg.Text(_("Provide web address of existing project")),
                    sg.InputText(self.props.project_url, k="project_url"),
                ]

            elements.append(project_input)
            if self.props.new_existing == "existing":
                elements.append(
                    [
                        sg.Text(
                            _(
                                "example: https://gitlab.com/gladykov/"
                                "example-project-for-crowd-law"
                            ),
                            text_color="grey",
                        )
                    ]
                )

        elements.append(
            [sg.Button(_("Next"), k="next"), sg.CloseButton(_("Cancel"), k="close")]
        )

        return sg.Frame(_("Welcome to Crowd Law app"), elements, font=("Helvetica", 25))

    def git_details(self, update=False):
        """
        Provide Git details - username, token

        Args:
            update: bool; when True we update existing data

        Returns:
            Frame
        """
        horizontal_line = [sg.HorizontalSeparator()]

        elements = [[menu_toolbar()]]

        select_git_provider = [
            [
                sg.Text(
                    _(
                        "In order to work with this tool, "
                        "you will need account on Git site. "
                        "It will take you only a moment."
                    )
                )
            ],
            [
                sg.Text(_("Select Git site")),
                sg.Combo(
                    values=self.props.supported_git_providers,
                    default_value=_(self.props.git_provider or None),
                    size=(20, 1),
                    k="git_provider",
                    readonly=True,
                    disabled=(self.props.new_existing == "existing"),
                    enable_events=True,
                ),
            ],
        ]

        if not update:
            for i in select_git_provider:
                elements.append(i)

            elements.append(horizontal_line)

        username_token = [
            [
                sg.Text(
                    _("Provide {git} username").format(
                        git=self.props.git_provider or "gitlab"
                    ),
                    k="username_label",
                ),
                sg.InputText(self.props.username, k="username_input", disabled=update),
                sg.Text(
                    _("No account? Create now."),
                    k="click_create_account",
                    enable_events=True,
                ),
            ],
            [
                sg.Text(
                    _("Provide {git_provider} token").format(
                        git_provider=self.props.git_provider or "gitlab"
                    ),
                    key="token_label",
                ),
                sg.InputText(self.props.token, k="token_input"),
                sg.Text(
                    _("Obtain token"), key="click_obtain_token", enable_events=True
                ),
                help_icon_clickable("show_gitlab_help"),
            ],
            [
                sg.Text(_("Provide token name"), k="token_name_label"),
                sg.InputText(self.props.token_name, k="token_name_input"),
            ],
        ]

        for element in username_token:
            elements.append(element)

        if update:
            elements.append(
                [
                    sg.Button(_("Update token info"), k="update"),
                    sg.Text("", size=(50, 1), text_color="red", k="token_error"),
                ]
            )
        else:
            elements.append(
                [
                    sg.Button(_("Back"), k="back"),
                    sg.CloseButton(_("Cancel"), k="close"),
                    sg.Button(_("Start!"), k="start"),
                    sg.Text("", size=(50, 1), text_color="red", k="token_error"),
                ]
            )

        return sg.Frame(_("Git details"), elements, font=("Helvetica", 25))
