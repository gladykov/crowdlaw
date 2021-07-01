import PySimpleGUI as sg


folder_icon = b"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABnUlEQVQ4y8WSv2rUQRSFv7vZgJFFsQg2EkWb4AvEJ8hqKVilSmFn3iNvIAp21oIW9haihBRKiqwElMVsIJjNrprsOr/5dyzml3UhEQIWHhjmcpn7zblw4B9lJ8Xag9mlmQb3AJzX3tOX8Tngzg349q7t5xcfzpKGhOFHnjx+9qLTzW8wsmFTL2Gzk7Y2O/k9kCbtwUZbV+Zvo8Md3PALrjoiqsKSR9ljpAJpwOsNtlfXfRvoNU8Arr/NsVo0ry5z4dZN5hoGqEzYDChBOoKwS/vSq0XW3y5NAI/uN1cvLqzQur4MCpBGEEd1PQDfQ74HYR+LfeQOAOYAmgAmbly+dgfid5CHPIKqC74L8RDyGPIYy7+QQjFWa7ICsQ8SpB/IfcJSDVMAJUwJkYDMNOEPIBxA/gnuMyYPijXAI3lMse7FGnIKsIuqrxgRSeXOoYZUCI8pIKW/OHA7kD2YYcpAKgM5ABXk4qSsdJaDOMCsgTIYAlL5TQFTyUIZDmev0N/bnwqnylEBQS45UKnHx/lUlFvA3fo+jwR8ALb47/oNma38cuqiJ9AAAAAASUVORK5CYII="


class MainWindowUI:
    def __init__(self, controller_props):
        self.props = controller_props
        sg.theme(self.props.theme)

    def repo_info(self):
        return sg.Frame(
            _("Server info"),
            [
                [sg.Text(_(f"URL: {self.props.project_url}"))],
                [sg.Text(_(f"User: {self.props.username}"), k="user")],
                [sg.Text(_(f"Token: **********"), k="token")],
                [sg.Text(_(f"Token name: token name"), k="token_name")],
                [sg.Button(_(f"Update token info"), k="update_token_info")],
            ],
            font=("Helvetica", 25),
        )

    def documents_list(self):
        return sg.Frame(
            _("Documents"),
            [
                [sg.Text("Click document to start editing")],
                [
                    sg.Tree(
                        headings=[
                            "Size",
                        ],
                        data=self.props.list_of_files,
                        key="doctree",
                        num_rows=20,
                        col0_width=40,
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

    def ok(ok):
        pass

    def stage(self):
        return sg.Frame("Current stage", [[sg.Text("Current stage")]])

    def editor_background_color(self):
        return 'grey' if self.props.editor_disabled else 'white'

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
                        background_color=self.editor_background_color()
                    )
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
