import os

from git import Repo, rmtree

from src.utils.utils import get_project_root

import logging

logger = logging.getLogger("root")
repo_root = os.path.join(get_project_root(), "repos", "base_repo")


class GitAdapter:
    def __init__(self, path, initialized=True):
        self.path = path
        if initialized:
            self.repo = Repo(self.path)
        else:
            self.initialize_repo()
            self.repo = Repo(self.path)

    def get_config(self, section, value):
        return self.repo.config_reader().get_value(section, value)

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

    def changes_exist(self):
        return bool(self.repo.git.ls_files(["-o", "-m", "--exclude-standard"]))

    def push(self):
        logger.info(f"Pushing changes to {self.repo.head.name}")
        self.repo.git.push("--set-upstream", "origin", self.repo.head.name)

    def pull(self):
        logger.info(f"Pulling changes to {self.repo.head.name}")
        self.repo.git.pull()

    def clone(self, local_path, remote_path):
        logger.info(f"Cloning from {remote_path} to {local_path}")
        self.repo.git.clone_from(remote_path, local_path)

    def local_branches(self):
        return sorted(list(map(lambda x: x.name, self.repo.heads)))

    def checkout_new_branch(self, branch_name):
        logger.info(f"Checking out new branch {branch_name}")
        self.repo.git.checkout(["-b", branch_name])

    def checkout_master(self):
        logger.info(f"Checkout master")
        self.repo.git.checkout(["master"])

    def checkout_existing_branch(self, branch_name):
        logger.info(f"Checking out existing branch {branch_name}")
        self.repo.git.checkout(branch_name)

    def remove_branch(self, branch_name):
        logger.info(f"Attempting to remove branch {branch_name}")
        branch_to_del = list(filter(lambda x: x.name == branch_name, self.repo.heads))
        assert (
            len(branch_to_del) == 1
        ), "Didn't found branch to delete of found too much"
        self.repo.delete_head(branch_to_del[0], force=True)
        logger.info(f"Branch removed {branch_name}")

    def remove_repo(self):
        logger.info(f"Attempting to remove repo {self.path}")
        rmtree(self.path)
        logger.info(f"Remove repo.")


if __name__ == "__main__":
    ga = GitAdapter(repo_root)
    ga.add_changed()
    ga.commit("new_commit")
    ga.push()
    # ga.add_all_untracked()
