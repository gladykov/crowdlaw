import gitlab
import os
import time
import gettext

from src.utils.utils import get_project_root, unzip_file, get_unpacked_repo_root

locale_dir = os.path.join(get_project_root(), "locale")

lang_en = gettext.translation('crowdlaw', localedir=locale_dir, languages=['en'])
lang_pl = gettext.translation('crowdlaw', localedir=locale_dir, languages=['pl'])
lang_pl.install()


class GitlabAPI:

    def __init__(self, user=None, token=None):
        if token is None:
            token = "BnEQx3xVq6xRzoxS7gKc"
        if user is None:
            self.user = "gladykov"
        else:
            self.user = user
        self.gl = gitlab.Gitlab('https://gitlab.com', private_token=token)
        self.gl.auth()

    def get_project_by_user_path(self, username, project_path):
        return self.gl.projects.get(username + "/" + project_path)

    def get_project_info(self, project):
        return {
            'username': project.owner['username'],
            'user_name': project.owner['name'],
            'email': project.users.gitlab.user.email,
            'repo_name': project.name,
            'repo_git_url': project.http_url_to_repo,
            'repo_web_url': project.web_url,
            'path': project.path,
        }

    def fork_project(self, project, new_name=None, new_path=None):
        name = new_name if new_name else project.name
        path = new_path if new_path else project.path
        project.forks.create({"name": name, "path": path})
        forked_project = self.get_project_by_user_path(self.user, path)
        print(_("Waiting for fork to complete. Grab a coffee."))
        while forked_project.import_status == 'started':
            print(_("waiting"))
            time.sleep(5)
            forked_project = self.get_project_by_user_path(self.user, path)

        return forked_project

    def update_project_name_path(self, project, new_name, new_path):
        self.gl.projects.update(project.id, {"name": new_name, "path": new_path})

    def download_project_archive(self, project):
        output_path = os.path.join(get_project_root(), 'tmp', 'archive.zip')
        file = self.gl.http_get(f"/projects/{project.id}/repository/archive.zip")
        with open(output_path, 'wb') as f:
            f.write(file.content)

        print(_(f"Downloaded project archive to {output_path}"))
        return output_path

    def upload_project_archive(self, project_name, archive_path):
        output = self.gl.projects.import_project(open(archive_path, 'rb'), project_name, overwrite=True)
        # Get a ProjectImport object to track the import status
        project_import = self.gl.projects.get(output['id'], lazy=True).imports.get()
        while project_import.import_status != 'finished':
            print(_("Waiting... importing... grab a cookie..."))
            time.sleep(5)
            project_import.refresh()
            if project_import.import_status == 'failed':
                print("import failed!")
                break

    def create_empty_project(self, project_name):
        return self.gl.projects.create({'name': project_name, 'visibility': 'public'})

    def prepare_archive_to_push(self, archive_path):
        os.path.join(get_project_root(), 'tmp', 'archive.zip')


if __name__ == "__main__":
    gl = GitlabAPI()
    # archive_path = gl.download_project_archive(gl.get_project_by_user_path(original_user, original_project))
    # gl.upload_project_archive("new_name3", archive_path)
    # forked_project = gl.fork_project(gl.get_project_by_user_path(original_user, original_project), "new_name", "new_path")
    # forked_project.delete_fork_relation()
    # gl.create_empty_project("empty_proj")
    # unzip_file(os.path.join(get_project_root(), 'tmp', 'archive.zip'))
    # dir_name, dir_path = get_unpacked_repo_root(original_project)
    # repo_root = os.path.join(get_project_root(), 'repos', 'base_repo')
    # os.rename(os.path.join(dir_path, dir_name), repo_root)
    forked_project = gl.get_project_by_user_path('gladykov', 'monopipeline')
    print(forked_project.import_status)
