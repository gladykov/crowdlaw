"""UI element of main view"""
import PySimpleGUI as sg

from crowdlaw.views.common import TITLE_FONT_SIZE, help_icon, menu_toolbar


LEFT_COLUMN_WIDTH = 280
CENTER_COLUMN_WIDTH = 700
RIGHT_COLUMN_WIDTH = 350


class MainWindowUI:
    """Main window of app, shown after on boarding"""

    def __init__(self, controller_props):
        self.props = controller_props
        sg.theme(self.props.theme)

    def contact_info(self):
        """
        Display contact info, for all team members.

        Returns:
            Frame
        """
        clickable_text = (
            _("[edit contact info]")
            if self.props.contact_info
            else _("[add contact info]")
        )
        return sg.Frame(
            _("Contact info"),
            [
                [
                    sg.Text(self.props.contact_info, k="contact_info")
                    if self.props.contact_info
                    else sg.Text(
                        _("contact info not set by maintainer"), k="contact_info"
                    ),
                    help_icon(
                        _("Information about group contact provided by maintainer")
                    ),
                ],
                [
                    sg.Text(
                        clickable_text,
                        enable_events=True,
                        k="click_add_contact_info",
                    )
                    if self.props.is_owner
                    else sg.Text()
                ],
            ],
            font=("Helvetica", TITLE_FONT_SIZE),
            size=(LEFT_COLUMN_WIDTH, 90),
        )

    def server_info(self):
        """
        Display server info
        Returns:
            Frame
        """
        return sg.Frame(
            _("Server info"),
            [
                [
                    sg.Text(
                        _("URL: {url}").format(url=self.props.project_url),
                        enable_events=True,
                        k=f"URL {self.props.project_url}",
                    ),
                ],
                [
                    sg.Text(
                        _("[share url]"),
                        k="click_share_url",
                        enable_events=True,
                    ),
                    sg.Text(_("copied to clipboard"), visible=False, k="copied_info"),
                ],
                [sg.Text(_("User: {user}").format(user=self.props.username), k="user")],
                [
                    sg.Text(
                        _("Token: ********"),
                        k="token",
                    )
                ],
                [
                    sg.Text(
                        _("Token name: {token_name}").format(
                            token_name=self.props.token_name
                        ),
                        k="token_name",
                    )
                ],
                [
                    sg.Button(
                        _("Update token info"),
                        k="update_token_info",
                        disabled=self.props.demo_version,
                    )
                ],
            ],
            font=("Helvetica", TITLE_FONT_SIZE),
            size=(RIGHT_COLUMN_WIDTH, 200),
        )

    def project_info(self):
        """
        Display project info
        Returns:
            Frame
        """
        return sg.Frame(
            _("Project info"),
            [
                [
                    sg.Text(_("Current project")),
                    sg.Text(
                        _("[change project]"),
                        enable_events=True,
                        k="click_change_project",
                    ),
                    help_icon(
                        _(
                            "This is your main project, "
                            "where you collaborate with other people. "
                            "Project is kept on server, but can be edited locally. "
                            "When you will create your version, you will upload your "
                            "changes to the server for a review by other team members."
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
                ],
            ],
            font=("Helvetica", TITLE_FONT_SIZE),
            size=(LEFT_COLUMN_WIDTH, 90),
        )

    def documents_list(self):
        """
        Display document list
        Returns:
            Frame
        """
        return sg.Frame(
            _("Documents in the set"),
            [
                [sg.Text(_("Click document to start editing"))],
                [
                    sg.Tree(
                        headings=[],
                        data=self.props.list_of_files,
                        key="doctree",
                        num_rows=10,
                        col0_width=((LEFT_COLUMN_WIDTH // 10) - 1),
                        enable_events=True,
                        select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                    )
                ],
                [
                    sg.Button(_("Add new file"), k="add_file"),
                    sg.Button(_("Remove selected file"), k="remove_file"),
                ],
            ],
            font=("Helvetica", TITLE_FONT_SIZE),
        )

    def stage(self):
        """
        Display stage info
        Returns:
            Frame
        """
        help_stage = help_icon(_("This shows what is actual status of your project."))
        stage_list = []
        for stage_number, stage in self.props.stages.items():
            if stage["status"] == "completed":
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

        final_elements_list = (
            [
                stage_list,
                [
                    sg.Text(
                        _("[edit stage info]"),
                        k="click_edit_stage_info",
                        enable_events=True,
                    )
                ],
            ]
            if self.props.is_owner
            else [stage_list]
        )

        return sg.Frame(
            _("Project stage"),
            final_elements_list,
            font=("Helvetica", TITLE_FONT_SIZE),
            size=(CENTER_COLUMN_WIDTH, 80),
            k="frame_stage",
        )

    def editor_background_color(self):
        """
        Get editor background color, depending if it is disabled or enabled.
        Returns:
            str
        """
        return "grey" if self.props.editor_disabled else "white"

    def text_editor(self):
        """
        Mighty text editor itself
        Returns:
            Frame
        """
        frame = sg.Frame(
            _("Document editor"),
            [
                [sg.Button(_("Save"), k="save")],
                [
                    sg.Multiline(
                        default_text=self.props.editor_text,
                        size=(70, 25),
                        k="document_editor",
                        disabled=self.props.editor_disabled,
                        background_color=self.editor_background_color(),
                        font=("Times New Roman", 12),
                    )
                ],
            ],
            font=("Helvetica", TITLE_FONT_SIZE),
            k="frame_document_editor",
        )
        return frame

    def branch_selector(self):
        """
        Dropdown select to select branch (working set)
        Returns:
            Frame
        """
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
                    help_icon(
                        _(
                            "In one project you can prepare multiple versions of "
                            "proposed changes. "
                            "Each version is called set of changes (or branch). "
                            "You can work on different sets of changes in parallel."
                        )
                    ),
                ],
                [
                    sg.Button(_("Add new set"), k="add_new_set"),
                    sg.Button(_("Remove set"), k="remove_set"),
                ],
            ],
            font=("Helvetica", TITLE_FONT_SIZE),
            size=(LEFT_COLUMN_WIDTH, 90),
        )

        return frame

    def online_reviews(self):
        """
        Show links to merge requests.
        Returns:
            Frame
        """
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
                sg.Button(
                    _("Send working set for a review"),
                    k="send_to_review",
                    disabled=not self.props.remote_api.connected
                    or self.props.demo_version,
                ),
                help_reviews,
            ]
            if self.props.merge_request is None
            else [
                sg.Button(
                    _("Update current review"),
                    k="update_review",
                    disabled=not self.props.remote_api.connected
                    or self.props.demo_version,
                ),
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
            else [sg.Text("", k="review_info")]
        )

        elements = [
            button,
            text,
        ]

        if self.props.demo_version:
            elements.insert(
                1,
                [sg.Text(_("Working in demo version. You cannot upload your changes"))],
            )

        return sg.Frame(
            _("Reviews"),
            elements,
            font=("Helvetica", TITLE_FONT_SIZE),
            size=(RIGHT_COLUMN_WIDTH, 120),
        )

    @staticmethod
    def change_project_popup():
        """
        Popup to add / remove project

        Returns:
            str
        """
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

    def add_contact_info_popup(self):
        """
        Add / edit contact info

        Returns:
            tuple(list, dict)
        """
        return sg.Window(
            _("Add / edit contact info"),
            [
                [
                    sg.Text(
                        _(
                            "Provide contact info (Whatsapp group, FB group, mailing "
                            "list, etc), where all participants can communicate with "
                            "each other"
                        ),
                    ),
                ],
                [
                    sg.Input(k="contact_info", default_text=self.props.contact_info),
                ],
                [
                    sg.Button(_("Add / edit contact info"), k="add_contact_info"),
                    sg.Button(_("Cancel"), k="cancel"),
                ],
            ],
            modal=True,
        ).read(close=True)

    def edit_stage_info(self):
        """
        Stage info editor

        Returns:
            Window
        """
        element_list = [
            [
                sg.Text(_("Active\nstage")),
                sg.Text(_("Stage name")),
                sg.Text(_("Remove stage")),
            ]
        ]

        for stage_number, stage in self.props.stages.items():
            element_list.append(
                [
                    sg.Radio(
                        "",
                        "current",
                        k=f"stage_is_active_{stage_number}",
                        default=(stage["status"] == "active"),
                    ),
                    sg.Input(
                        default_text=stage["name"],
                        k=f"stage_name_{stage_number}",
                        size=(30, 10),
                    ),
                    sg.Button("-", k=f"remove_stage_{stage_number}"),
                ]
            )

        return sg.Window(
            _("Edit stage info"),
            [
                [
                    sg.Col(
                        element_list,
                        size=(400, 300),
                        scrollable=True,
                        vertical_scroll_only=True,
                        k="stages_col",
                    )
                ],
                [
                    sg.Button(_("Add stage"), k="add_stage"),
                    sg.Button(_("Mark all as done"), k="all_done"),
                    sg.Button(_("Save"), k="save"),
                    sg.Button(_("Cancel"), k="cancel"),
                ],
                [sg.Text("", k="error", size=(40, 1), text_color="red")],
            ],
            finalize=True,
            size=(450, 380),
        )

    def layout(self):
        """
        Holy layout of main window

        Returns:
            list
        """
        left_col = sg.Column(
            [
                [self.project_info()],
                [sg.HorizontalSeparator()],
                [self.branch_selector()],
                [self.documents_list()],
                [self.contact_info()],
            ],
            vertical_alignment="top",
        )

        center_col = sg.Column(
            [
                [self.stage()],
                [sg.HorizontalSeparator()],
                [self.text_editor()],
            ],
            vertical_alignment="top",
            k="center_column",
        )

        right_col = sg.Column(
            [
                [self.server_info()],
                [sg.HorizontalSeparator()],
                [self.online_reviews()],
            ],
            vertical_alignment="top",
        )

        layout = [
            [menu_toolbar()],
            [
                left_col,
                sg.VerticalSeparator(),
                center_col,
                sg.VerticalSeparator(),
                right_col,
            ],
        ]

        return layout
