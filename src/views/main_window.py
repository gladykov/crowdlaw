import PySimpleGUI as sg


class MainWindowUI:
    def __init__(self, controller_props):
        self.props = controller_props
        sg.theme(self.props.theme)

    def repo_info(self):
        return sg.Frame(
            _("Project info"),
            [
                [sg.Text(_(f"URL: {self.props.project_url}"))],
                [sg.Text(_(f"User: {self.props.username}"), k="user")],
                [sg.Text(_(f"Token: **********"), k="token")],
                [sg.Text(_(f"Token name: token name"), k="token_name")],
                [sg.Button(_(f"Update token info"), k="update_token_info")],
                self.project_selector(),
            ],
            font=("Helvetica", 25),
        )

    def project_selector(self):
        frame = [
            sg.Combo(
                self.props.projects,
                enable_events=True,
                default_value=self.props.project_name,
                k="project_selector",
            ),
            sg.Button(_("Add new project"), k="add_new_project"),
            sg.Button(_("Remove project"), k="remove_project"),
        ]

        return frame

    def documents_list(self):
        return sg.Frame(
            _("Documents"),
            [
                [sg.Text("Click document to start editing")],
                [
                    sg.Tree(
                        headings=[],
                        data=self.props.list_of_files,
                        key="doctree",
                        num_rows=10,
                        col0_width=20,
                        enable_events=True,
                        select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                    )
                ],
                [
                    sg.Button(_("Add new file"), k="add_file"),
                    sg.Button(_("Remove selected file"), k="remove_file"),
                ],
            ],
        )

    def stage(self):
        return sg.Frame("Current stage", [[sg.Text("Current stage")]])

    def editor_background_color(self):
        return "grey" if self.props.editor_disabled else "white"

    def text_editor(self):
        frame = sg.Frame(
            _("Document editor"),
            [
                [
                    sg.Multiline(
                        default_text=self.props.editor_text,
                        size=(60, 20),
                        k="document_editor",
                        disabled=self.props.editor_disabled,
                        background_color=self.editor_background_color(),
                    )
                ]
            ],
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
                ]
            ],
        )
        return frame

    def layout(self):
        left_col = sg.Column(
            [
                [self.repo_info()],
                [sg.HorizontalSeparator()],
                [self.documents_list()],
                [self.branch_selector()],
            ]
        )

        center_col = sg.Column(
            [
                [self.stage()],
                [sg.HorizontalSeparator()],
                [self.text_editor()],
                [sg.Button(_("Save"), k="save")],
            ]
        )

        layout = [
            [left_col, sg.VerticalSeparator(), center_col],
        ]

        return layout
