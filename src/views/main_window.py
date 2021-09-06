import PySimpleGUI as sg

from src.views.common import help_icon


title_font_size = 17


class MainWindowUI:
    """Main window of app, shown after on boarding"""
    def __init__(self, controller_props):
        self.props = controller_props
        sg.theme(self.props.theme)

    def server_info(self):
        return sg.Frame(
            _("Server info"),
            [
                [sg.Text(_(f"URL: {self.props.project_url}"))],
                [sg.Text(_(f"User: {self.props.username}"), k="user")],
                [
                    sg.Column(
                        [
                            [
                                sg.Text(
                                    _(f"Token: {len(self.props.token) * '*'}"),
                                    k="token",
                                )
                            ],
                            [
                                sg.Text(
                                    _(f"Token name: {self.props.token_name}"),
                                    k="token_name",
                                )
                            ],
                        ]
                    ),
                    sg.VerticalSeparator(),
                    sg.Column(
                        [
                            [sg.Button(_(f"Update token info"), k="update_token_info")],
                        ]
                    ),
                ],
            ],
            font=("Helvetica", title_font_size),
        )

    def project_info(self):
        return sg.Frame(
            _("Project info"),
            [
                [
                    sg.Text(_("Current project")),
                    help_icon(
                        _(
                            "This is your main project, where you collaborate with other people. "
                            "Project is kept on server, but can be edited locally. "
                            "When you will create your version, you will upload your changes to the server for a review by other team members."
                        ),
                    ),
                ],
                [
                    sg.Combo(
                        self.props.projects,
                        enable_events=True,
                        default_value=self.props.project_name,
                        k="project_selector",
                    ),
                    sg.Text(
                        _("[change project]"),
                        enable_events=True,
                        k="click_change_project",
                    ),
                ],
            ],
            font=("Helvetica", title_font_size),
        )

    def documents_list(self):
        return sg.Frame(
            _("Documents in the set"),
            [
                [sg.Text("Click document to start editing")],
                [
                    sg.Tree(
                        headings=[],
                        data=self.props.list_of_files,
                        key="doctree",
                        num_rows=10,
                        col0_width=30,
                        enable_events=True,
                        select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                    )
                ],
                [
                    sg.Button(_("Add new file"), k="add_file"),
                    sg.Button(_("Remove selected file"), k="remove_file"),
                ],
            ],
            font=("Helvetica", title_font_size),
        )

    def stage(self):
        help_stage = help_icon("This shows what is actual status of your project.")
        stage_list = []
        for stage_number, stage in self.props.stages.items():
            if stage["status"] == "finished":
                stage_element = sg.Text(
                    f"{stage_number}. " + stage["name"], font="tahoma 10 overstrike"
                )
            elif stage["status"] == "future":
                stage_element = sg.Text(
                    f"{stage_number}. " + stage["name"],
                    font="tahoma 10",
                    text_color="grey",
                )
            elif stage["status"] == "active":
                stage_element = sg.Text(
                    f"{stage_number}. " + stage["name"], font="tahoma 10 bold"
                )
            else:
                raise ValueError(_("Unrecognized status of stage"))

            stage_list.append(stage_element)
            stage_list.append(sg.Text("🠒"))

        stage_list.pop(-1)
        stage_list.append(help_stage)

        return sg.Frame(
            "Project stage",
            [stage_list],
            font=("Helvetica", title_font_size),
        )

    def editor_background_color(self):
        return "grey" if self.props.editor_disabled else "white"

    def text_editor(self):
        frame = sg.Frame(
            _("Document editor"),
            [
                [
                    sg.Multiline(
                        default_text=self.props.editor_text,
                        size=(80, 20),
                        k="document_editor",
                        disabled=self.props.editor_disabled,
                        background_color=self.editor_background_color(),
                    )
                ]
            ],
            font=("Helvetica", title_font_size),
        )
        return frame

    def branch_selector(self):
        frame = sg.Frame(
            _("Sets of changes"),
            [
                [
                    sg.Combo(
                        self.props.branch_names,
                        enable_events=True,
                        default_value=self.props.branch_name,
                        k="branch_selector",
                    ),
                    sg.Button(_("Add new set"), k="add_new_set"),
                    sg.Button(_("Remove set"), k="remove_set"),
                    help_icon(
                        _(
                            "In one project you can prepare multiple versions of proposed changes. "
                            "Each version is called set of changes (or branch). "
                            "You can work on different sets of changes in pararell."
                        )
                    ),
                ]
            ],
            font=("Helvetica", title_font_size),
        )
        return frame

    def online_reviews(self):

        help_reviews = help_icon(
            _(
                "When you are ready to propose your changes, send them for a review. "
                "Other team members will review them. "
                "All reviews are done on remote server. "
                "Communication is done by email, so watch your inbox."
            )
        )

        button = (
            [
                sg.Button(_("Send working set for a review"), k="send_to_review"),
                help_reviews,
            ]
            if self.props.merge_request is None
            else [
                sg.Button(_("Update current review"), k="update_review"),
                help_reviews,
            ]
        )

        text = (
            [
                sg.Text(
                    self.props.merge_request,
                    enable_events=True,
                    k=f"URL {self.props.merge_request}",
                )
            ]
            if self.props.merge_request is not None
            else [sg.Text("")]
        )

        frame = sg.Frame(
            _("Reviews"),
            [
                button,
                text,
            ],
            font=("Helvetica", title_font_size),
        )
        return frame

    def layout(self):
        left_col = sg.Column(
            [
                [self.project_info()],
                [sg.HorizontalSeparator()],
                [self.branch_selector()],
                [self.documents_list()],
            ],
            vertical_alignment="top",
        )

        center_col = sg.Column(
            [
                [self.stage()],
                [sg.HorizontalSeparator()],
                [self.text_editor()],
                [sg.Button(_("Save"), k="save")],
            ],
            vertical_alignment="top",
        )

        right_col = sg.Column(
            [
                [self.server_info()],
                [sg.HorizontalSeparator()],
                [self.online_reviews()],
                [sg.HorizontalSeparator()],
                [
                    sg.Multiline(
                        size=(20, 30),
                        autoscroll=True,
                        auto_refresh=True,
                        reroute_stdout=False,
                        expand_x=True,
                        expand_y=True,
                        key="stdout",
                    )
                ],
            ],
            vertical_alignment="top",
        )

        layout = [
            [
                left_col,
                sg.VerticalSeparator(),
                center_col,
                sg.VerticalSeparator(),
                right_col,
            ],
        ]

        return layout

    @staticmethod
    def change_project_popup():
        return sg.Window(
            _("Change project"),
            [
                [
                    sg.Button(_("Add new project"), k="add_new_project"),
                    sg.Button(_("Remove project"), k="remove_project"),
                    sg.Button(_("Cancel"), k="cancel"),
                ],
            ],
            modal=True,
        ).read(close=True)[0]
