import os

import validators

from src.api.api import get_api
from src.git_adapter.git_adapter import GitAdapter
from src.model.base import Base
from src.utils.utils import get_project_root, strip_string


class OnBoardingModel(Base):
    def __init__(self):
        self.new_existing = None
        self.project_url = None
        self.project_name = None
        self.git_provider = None
        self.username = None
        self.token = None
        self.token_name = None
        self.theme = "DarkTeal6"  # Move to some common place
        self.supported_git_providers = list(self.git_providers().keys())
        self.config = self.get_config()

    def validate_page_1(self, values):
        issues = []
        if not values["new"] and not values["existing"]:
            issues.append(
                _("Please select if you want to join new or existing project")
            )
        if values["new"] and not values["project_name"]:
            issues.append(_("Provide project name"))
        if values["existing"] and not values["project_url"]:
            issues.append(_("Provide project URL"))
        if values["existing"] and values["project_url"]:
            if validators.url(values["project_url"]):
                found = False
                for provider in self.supported_git_providers:
                    if provider in values["project_url"]:
                        found = True
                        self.git_provider = provider
                        break
                if not found:
                    issues.append(_("Provided unsupported website URL"))
            else:
                issues.append(_("Provide valid project URL"))

        return issues if issues else True

    def collect_page_1(self, values):
        if values["new"]:
            self.project_name = values["project_name"]
        else:
            self.project_url = values["project_url"]
            self.project_name = values["project_url"].split("/")[-1].split(".")[0]
            print(self.project_name)

    @staticmethod
    def validate_page_2(values):
        issues = []
        if not values["username_input"]:
            issues.append(_("Provide username"))
        if not values["token_input"]:
            issues.append(_("Provide API token key"))
        if not values["token_name_input"]:
            issues.append(_("Provide API token key name"))

        return issues if issues else True

    def collect_page_2(self, values):
        self.username = values["username_input"]
        self.token = values["token_input"]
        self.token_name = values["token_name_input"]
        self.git_provider = values["git_provider"]

    def fill_credentials(self, window, git_provider):
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

        self.username = self.config["git_providers"][self.git_provider]["username"]
        self.token = self.config["git_providers"][self.git_provider]["token"]
        self.token_name = self.config["git_providers"][self.git_provider]["token_name"]
        window["username_input"].update(self.username)
        window["token_input"].update(self.token)
        window["token_name_input"].update(self.token_name)
        window.refresh()

        return True

    def open_create_git_account(self):
        self.open_url_in_browser(
            self.git_providers()[self.git_provider]["base_url"]
            + self.git_providers()[self.git_provider]["create_account"]
        )

    def open_obtain_token(self):
        self.open_url_in_browser(
            self.git_providers()[self.git_provider]["base_url"]
            + self.git_providers()[self.git_provider]["get_token"]
        )

    def initialize_project(self):
        RemoteAPI = get_api(self.git_provider, self.git_providers())
        remote_api = RemoteAPI(self.username, self.token)

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

        if self.config and self.project_name in self.config["projects"].keys():
            return [_(f"Project {self.project_name} already exists")]

        project_dir = os.path.join(
            get_project_root(), "projects", project_stripped_name
        )

        if not os.path.exists(project_dir):
            os.mkdir(project_dir)
        else:
            return [_(f"Project folder {project_dir} already exists")]

        if new_project:
            project = remote_api.get_project_info(
                remote_api.create_empty_project(self.project_name)
            )
        else:
            project_details = self.project_url.split("/")
            project_to_fork = remote_api.get_project_by_user_path(
                project_details[-2], project_details[-1]
            )
            forked_proj = remote_api.fork_project(project_to_fork)
            project = remote_api.get_project_info(forked_proj)

        username = project["username"]
        user_name = project["user_name"]
        email = project["email"]
        repo_name = project["repo_name"]
        repo_git_url = project["repo_git_url"]
        repo_web_url = project["repo_web_url"]
        path = project["path"]

        git_adapter = GitAdapter(project_dir, initialized=False)
        git_adapter.set_config("user", "name", user_name)
        git_adapter.set_config("user", "email", email)
        repo_git_url = remote_api.get_credentials_git_url(self.token_name, path)
        git_adapter.set_config('remote "origin"', "url", repo_git_url)

        if new_project:
            for example_file in ["example_1.txt", "example_2.txt", "example_3.txt"]:
                with open(os.path.join(project_dir, example_file), "w") as fp:
                    fp.write(_(f"Contents of {example_file}"))

            git_adapter.add_all_untracked()
            git_adapter.commit(_(f"Initial commit for project {self.project_name}"))
            git_adapter.push()
        else:
            git_adapter.pull()

        # And now we can write config
        project_dict = {
            "nice_name": repo_name,
            "provider": self.git_provider,
            "username": username,
            "project_url": repo_web_url,
            "is_owner": new_project,
            "folder": project_dir,
        }

        if not self.config:
            self.config = {
                "init": True,
                "projects": {},
                "lang": "en",  # TODO: Set and Get current language during on boarding
                "git_providers": {},
            }

        # Always update to latest for given provider
        self.config["git_providers"][self.git_provider] = {
            "username": self.username,
            "token": self.token,
            "token_name": self.token_name,
        }
        self.config["projects"][self.project_name] = project_dict
        self.config["last_project"] = self.project_name

        self.set_config(self.config)
        return True