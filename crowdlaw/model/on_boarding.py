"""On boarding module"""
import os
import shutil

import validators

from crowdlaw.api.api import get_api
from crowdlaw.git_adapter.git_adapter import GitAdapter
from crowdlaw.model.common import BaseModel
from crowdlaw.utils.utils import (
    get_project_root,
    get_projects_path,
    strip_string,
    super_init,
)


class OnBoardingModel(BaseModel):
    """
    Used when configuring app for the first time to use with Git
    repo and also when updating token info across all repos
    """

    @super_init
    def __init__(self):
        self.new_existing = None
        self.project_url = None
        self.project_name = None
        self.git_provider = None
        self.username = None
        self.token = None
        self.token_name = None
        self.supported_git_providers = list(self.git_providers().keys())
        self.config = self.get_config()

    def validate_page_1(self, values):
        """
        Check if first window was filled properly.

        Args:
            values: dict - all values from first window

        Returns:
            bool, list - True when everything is OK, list if found some issues
        """
        issues = []
        if not values["new"] and not values["existing"]:
            issues.append(
                _("Please select if you want to create new or join existing project")
            )
        if values["new"] and not values["project_name"]:
            issues.append(_("Provide project name"))
        if values["existing"] and not values["project_url"]:
            issues.append(_("Provide project web address"))
        if values["existing"] and values["project_url"]:
            if validators.url(values["project_url"]):
                found = False
                for provider in self.supported_git_providers:
                    if provider in values["project_url"]:
                        found = True
                        self.git_provider = provider
                        break
                if not found:
                    issues.append(_("Provided unsupported Git provider"))
            else:
                issues.append(_("Provide valid web address of a project"))

        return issues if issues else True

    def collect_page_1(self, values):
        """
        Sets properties based on data entered in first window

        Args:
            values: dict

        Returns:
            None
        """
        if values["new"]:
            self.project_name = values["project_name"]
        else:
            self.project_url = values["project_url"].strip().rstrip("/")
            self.project_name = self.project_url.split("/")[-1].split(".")[0]

    @staticmethod
    def validate_page_2(values):
        """
        Check if 2nd window was filled properly.

        Args:
            values: dict - all values from 2nd window

        Returns:
            bool, list - True when everything is OK, list if found some issues
        """
        issues = []
        if not values["username_input"]:
            issues.append(_("Provide username"))
        if not values["token_input"]:
            issues.append(_("Provide API token key"))
        if not values["token_name_input"]:
            issues.append(_("Provide API token key name"))

        return issues if issues else True

    def collect_page_2(self, values):
        """
        Sets properties based on data entered in 2nd window

        Args:
            values: dict

        Returns:
            None
        """
        self.username = values["username_input"].strip()
        self.token = values["token_input"].strip()
        self.token_name = values["token_name_input"].strip()
        self.git_provider = values["git_provider"].strip()

    def fill_credentials(self, window, git_provider):
        """
        Fill credentials info in credentials fields for given provider.

        Args:
            window: window
            git_provider: str

        Returns:
            bool - True if credentials were filled, otherwise False
        """
        window["username_input"].update("")
        window["token_input"].update("")
        window["token_name_input"].update("")
        self.username = None
        self.token = None
        self.token_name = None
        window.refresh()
        self.git_provider = git_provider

        if self.config.get("git_providers") is None:
            return False

        if self.config["git_providers"].get(git_provider) is None:
            return False

        username = self.config["git_providers"][self.git_provider]["username"]
        token_name = self.config["git_providers"][self.git_provider]["token_name"]
        if username == "gladykov" and token_name == "crowdlaw_read_only":
            return False  # Demo version

        self.username = username
        self.token = self.config["git_providers"][self.git_provider]["token"]
        self.token_name = token_name
        window["username_input"].update(self.username)
        window["token_input"].update(self.token)
        window["token_name_input"].update(self.token_name)
        window.refresh()

        return True

    def open_create_git_account(self):
        """Open create account page in browser"""
        self.open_url_in_browser(
            self.git_providers()[self.git_provider]["base_url"]
            + self.git_providers()[self.git_provider]["create_account"]
        )

    def open_obtain_token(self):
        """Open obtain token page in browser"""
        self.open_url_in_browser(
            self.git_providers()[self.git_provider]["base_url"]
            + self.git_providers()[self.git_provider]["get_token"]
        )

    def initialize_project(self):
        """
        Set all properties and configs needed to work with project,
        based on user input.
        """
        RemoteAPI = get_api(self.git_provider, self.git_providers())
        remote_api = RemoteAPI(self.username, self.token)

        if not remote_api.authenticated:
            return [_("I was not able to authenticate using credentials provided")]

        new_project = self.new_existing == "new"
        project_stripped_name = strip_string(self.project_name)

        if new_project:
            self.project_url = "/".join(
                [
                    self.git_providers()[self.git_provider]["base_url"],
                    self.username,
                    project_stripped_name,
                ]
            )

        if (
            self.config
            and "projects" in self.config.keys()
            and self.project_name in self.config["projects"].keys()
        ):
            return [
                _("Project {project_name} already exists").format(
                    project_name=self.project_name
                )
            ]

        project_dir = os.path.join(get_projects_path(), project_stripped_name)

        if not os.path.exists(project_dir):
            os.mkdir(project_dir)
        else:
            return [
                _("Project folder {project_dir} already exists").format(
                    project_dir=project_dir
                )
            ]

        if new_project:
            is_owner = True
            project = remote_api.get_project_info(
                remote_api.create_empty_project(self.project_name)
            )
        else:
            project_details = self.project_url.split("/")
            source_project = remote_api.get_project_by_user_path(
                project_details[-2], project_details[-1]
            )
            # We may be owner of existing we are joining, after some break
            if project_details[-2] == self.username:
                is_owner = True
                project = remote_api.get_project_info(source_project)
            else:
                is_owner = False
                # TODO: After some break we may want to join our existing fork
                forked_proj = remote_api.fork_project(source_project)
                if forked_proj == "error":
                    os.rmdir(project_dir)
                    return [
                        _(
                            "There was an error while creating copy of the project on"
                            " your server. "
                            "Probably project {project_name} already exists"
                            " on your server."
                        ).format(project_name=project_details[-1])
                    ]
                project = remote_api.get_project_info(forked_proj)

        username = project["username"]
        user_name = project["user_name"]
        email = project["email"]
        repo_name = project["repo_name"]
        repo_web_url = project["repo_web_url"]
        path = project["path"]

        git_adapter = GitAdapter(project_dir, initialized=False)
        git_adapter.set_config("user", "name", user_name)
        git_adapter.set_config("user", "email", email)
        repo_git_url = remote_api.get_credentials_git_url(self.token_name, path)
        git_adapter.set_config('remote "origin"', "url", repo_git_url)
        git_adapter.set_config(
            'remote "origin"', "fetch", "+refs/heads/*:refs/remotes/origin/*"
        )

        if new_project:
            for example_file in ["example_1.txt", "example_2.txt", "example_3.txt"]:
                with open(os.path.join(project_dir, example_file), "w") as file:
                    file.write(
                        _("Contents of {example_file}").format(
                            example_file=example_file
                        )
                    )

            shutil.copy(
                os.path.join(get_project_root(), "resources", "stages.yaml"),
                os.path.join(project_dir, "stages.yaml"),
            )

            git_adapter.add_all_untracked()

            git_adapter.commit(
                _("Initial commit for project {project_name}").format(
                    project_name=self.project_name
                )
            )
            git_adapter.push()
        else:
            if is_owner:
                git_adapter.localise_remote_branches()
            else:
                # For existing origin, which we are not owners, we fork.
                # TODO: Detect default branch and remove all other remote branches
                #  from fork not to pollute user
                git_adapter.localise_remote_branch("master")
                git_adapter.checkout_existing_branch("master")

        # And now we can write config
        project_dict = {
            "nice_name": repo_name,
            "provider": self.git_provider,
            "username": username,
            "project_url": repo_web_url,
            "is_owner": is_owner,
            "folder": project_dir,
        }

        # At this moment at least language is already selected
        if self.config["init"] is False:
            self.config = {
                "projects": {},
                "git_providers": {},
            } | self.config

            self.config["init"] = True

        # Always update to latest credentials for given provider
        self.config["git_providers"][self.git_provider] = {
            "username": self.username,
            "token": self.token,
            "token_name": self.token_name,
        }
        self.config["projects"][project_stripped_name] = project_dict
        self.config["last_project"] = project_stripped_name

        self.set_config(self.config)
        return True
