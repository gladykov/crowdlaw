import os

from git import Repo, rmtree

from src.utils.utils import get_project_root


repo_root = os.path.join(get_project_root(), "repos", "base_repo")


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

    def local_branches(self):
        local_branches = []
        for head in self.repo.heads:
            local_branches.append(head.name)

        return local_branches

    def checkout_new_branch(self, branch_name):
        self.repo.git.checkout(f"-b{branch_name}")  # Sth adds space in front of name

    def checkout_existing_branch(self, branch_name):
        self.repo.git.checkout(branch_name)

    def remove_repo(self):
        rmtree(self.path)


if __name__ == "__main__":
    ga = GitAdapter(repo_root)
    ga.add_changed()
    ga.commit("new_commit")
    ga.push()
    # ga.add_all_untracked()
