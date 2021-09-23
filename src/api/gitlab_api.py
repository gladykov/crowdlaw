import logging
import time

import gitlab


logger = logging.getLogger("root")


class GitlabAPI:
    """Main class handling communication with Gitlab servers"""

    def __init__(self, user=None, token=None):
        self.authenticated = False
        if token is None:
            self.token = "MwJxgVNCdBcQ8Nk6zy6R"
        else:
            self.token = token
        if user is None:
            self.user = "gladykov"
        else:
            self.user = user
        self.gl = gitlab.Gitlab("https://gitlab.com", private_token=token)
        try:
            self.gl.auth()
            logger.info("Successfully authenticated")
            self.authenticated = True

        except gitlab.exceptions.GitlabAuthenticationError:
            logger.error("Not authenticated")
        self.project = None

    def set_current_project(self, username, project_path):
        """
        Set Gitlab project we are working on.

        Args:
            username: str
            project_path: str - gitlab url project name

        Returns:

        """
        self.project = self.get_project_by_user_path(username, project_path)

    def get_project_by_user_path(self, username, project_path):
        """
        Get project by username and path, ex: gladykov/crowdlaw

        Args:
            username: str
            project_path: str

        Returns:

        """
        return self.gl.projects.get(username + "/" + project_path)

    @staticmethod
    def get_project_info(project):
        """
        Get various properties of a Gitlab project

        Args:
            project: gitlab project

        Returns:
            dict
        """
        return {
            "username": project.owner["username"],
            "user_name": project.owner["name"],
            "email": project.users.gitlab.user.email,
            "repo_name": project.name,
            "repo_git_url": project.http_url_to_repo,
            "repo_web_url": project.web_url,
            "path": project.path,
        }

    def fork_project(self, project, new_name=None, new_path=None):
        """
        Fork existing project

        Args:
            project: existing project
            new_name: name for new project
            new_path: path of new project

        Returns:
            project
        """
        name = new_name if new_name else project.name
        path = new_path if new_path else project.path
        project.forks.create({"name": name, "path": path})
        forked_project = self.get_project_by_user_path(self.user, path)
        logger.info(_("Waiting for fork to complete. Grab a coffee."))
        while forked_project.import_status == "started":
            logger.info(_("waiting"))
            time.sleep(5)
            forked_project = self.get_project_by_user_path(self.user, path)

        return forked_project

    def update_project_name_path(self, project, new_name, new_path):
        """
        Updates project name and path

        Args:
            project: gitlab project
            new_name: str
            new_path: str

        Returns:
            None
        """
        self.gl.projects.update(project.id, {"name": new_name, "path": new_path})

    def create_empty_project(self, project_name):
        """
        Creates empty project

        Args:
            project_name: str

        Returns:
            project
        """
        return self.gl.projects.create({"name": project_name, "visibility": "public"})

    def get_credentials_git_url(self, token_name, path):
        return f"https://{token_name}:{self.token}@gitlab.com/{self.user}/{path}.git"

    @staticmethod
    def get_base_project_id(project):
        """
        Get ID of base project

        Args:
            project:

        Returns:
            str
        """
        return (
            project.forked_from_project["id"]
            if hasattr(project, "forked_from_project")
            else project.id
        )

    def create_merge_request(
        self, username, project_path, source_branch, target_branch, title
    ):
        """
        Create merge request

        Args:
            username: str
            project_path: str
            source_branch: str
            target_branch: str
            title: str

        Returns:
            result
        """
        project = self.get_project_by_user_path(username, project_path)

        result = project.mergerequests.create(
            {
                "source_branch": source_branch,
                "target_branch": target_branch,
                "title": title,
                "target_project_id": self.get_base_project_id(project),
            }
        )
        return result

    def get_merge_requests(self, author, source_branch):
        """
        Get merge requests of current user

        Args:
            author: str
            source_branch: str

        Returns:
            list
        """
        project = self.gl.projects.get(self.get_base_project_id(self.project))
        listmr = project.mergerequests.list(
            state="opened",
            source_branch=source_branch,
            author_username=author,
        )
        return listmr

    def get_branches(self):
        """
        Get branches from current project

        Returns:
            list
        """
        return list(map(lambda x: x.name, self.project.branches.list()))
