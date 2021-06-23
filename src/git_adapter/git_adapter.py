import os

from src.utils.utils import get_project_root

from git import Repo

repo_root = os.path.join(get_project_root(), 'repos', 'base_repo')


class GitAdapter:

    def __init__(self, path, initialized=True):
        self.path = path
        if initialized:
            self.repo = Repo(self.path)
        else:
            self.initialize_repo()
            self.repo = Repo(self.path)

    def get_config(self):
        return self.repo.config_reader()

    def set_config(self, section, variable, value):
        with self.repo.config_writer() as config:
            config.set_value(section, variable, value)

    def initialize_repo(self):
        self.repo = Repo.init(self.path)

    def add_all_untracked(self):
        self.repo.git.add("-A")

    def add_changed(self):
        self.repo.git.add("-u")

    def commit(self, commit_message):
        self.repo.git.commit(f"-m {commit_message}")

    def push(self):
        self.repo.git.push()

    def pull(self):
        self.repo.git.pull()

    def clone(self, local_path, remote_path):
        self.repo.git.clone_from(remote_path, local_path)

if __name__ == "__main__":
    ga = GitAdapter(repo_root)
    ga.add_changed()
    ga.commit("new_commit")
    ga.push()
    # ga.add_all_untracked()
