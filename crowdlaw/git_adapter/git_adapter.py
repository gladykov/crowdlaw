"""Local Git manipulations with GitPython and native Git"""
import logging

from git import Repo, rmtree

from crowdlaw.utils.utils import strip_string


logger = logging.getLogger("root")


class GitAdapter:
    """
    Class to handle local Git program
    """

    def __init__(self, path, initialized=True):
        self.path = path
        self.master_shas = set()
        if initialized:
            self.repo = Repo(self.path)
        else:
            self.initialize_repo()

    def get_config(self, section, value):
        """
        Get single value from Git config

        Args:
            section: str
            value: str

        Returns:
            str
        """
        return self.repo.config_reader().get_value(section, value)

    def set_config(self, section, variable, value):
        """
        Write single value to Git config

        Args:
            section: str
            variable: str
            value: str

        Returns:
            None
        """
        with self.repo.config_writer() as config:
            config.set_value(section, variable, value)

    def initialize_repo(self):
        """
        Initialize local repo object

        Returns:
            None
        """
        self.repo = Repo.init(self.path)

    def add_all_untracked(self):
        """
        Add all untracked files to staging

        Returns:
            None
        """
        self.repo.git.add("-A")

    def add_changed(self):
        """
        Add only changed tracked files to staging

        Returns:
            None
        """
        self.repo.git.add("-u")

    def commit(self, commit_message):
        """
        Commit changes

        Args:
            commit_message: str

        Returns:
            None
        """
        self.repo.git.commit(f"-m {commit_message}")

    def changes_exist(self):
        """
        Check if there are unstaged changed in repo

        Returns:
            bool
        """
        return bool(self.repo.git.ls_files(["-o", "-m", "--exclude-standard"]))

    def push(self):
        """
        Push changes to server

        Returns:
            None
        """
        logger.info(f"Pushing changes to {self.repo.head.name}")
        self.repo.git.push("--set-upstream", "origin", self.repo.head.name)

    def pull(self):
        """
        Pull changes from server

        Returns:
            None
        """
        logger.info(f"Pulling changes to {self.repo.head.name}")
        self.repo.git.pull()

    def clone(self, local_path, remote_path):
        """
        Clone repo

        Args:
            local_path: str
            remote_path: str

        Returns:
            None
        """
        logger.info(f"Cloning from {remote_path} to {local_path}")
        self.repo.git.clone_from(remote_path, local_path)

    def local_branches(self):
        """
        List local branches (except master)

        Returns:
            list
        """
        local_branches = sorted(list(map(lambda x: x.name, self.repo.heads)))
        if "master" in local_branches:
            local_branches.remove("master")

        return local_branches

    def checkout_new_branch(self, branch_name):
        """
        Checkout new local branch

        Args:
            branch_name: str

        Returns:
            None
        """
        branch_name = strip_string(branch_name)
        logger.info(f"Checking out new branch {branch_name}")
        self.repo.git.checkout(["-b", branch_name])

    def checkout_master(self):
        """
        Checkout master branch

        Returns:
            None
        """
        logger.info("Checkout master")
        self.repo.git.checkout(["master"])

    def checkout_existing_branch(self, branch_name):
        """
        Checkout existing local branch

        Args:
            branch_name: str

        Returns:
            None
        """
        logger.info(f"Checking out existing branch {branch_name}")
        self.repo.git.checkout(branch_name)

    def localise_remote_branches(self):
        """
        When new origin is added, we know nothing about remote branches.
        Make all remote branches available as local branches,
        whose author of first commit was current user

        Args:

        Returns:
            None
        """
        self.repo.remotes.origin.fetch()
        origin = self.repo.remotes.origin

        # Collect all SHAs of commits from master
        for parent_commit in self.repo.iter_commits("origin/master"):
            self.master_shas.add(parent_commit.hexsha)

        for branch in self.repo.remote().refs:
            branch_name = branch.name.split("/")[1]
            if branch_name == "master":  # Always localise master
                pass
            else:
                # Only localise branches with current author
                if self.branch_author_email(branch_name) != self.get_config(
                    "user", "email"
                ):
                    continue

            self.repo.create_head(
                branch_name, branch
            )  # create local branch "x" from remote "x"
            self.repo.heads.__getattr__(branch_name).set_tracking_branch(
                origin.refs.__getattr__(branch_name)
            )  # Set tracking information

    def branch_author_email(self, branch_name):
        """
        Get email of commiter, of first commit which is not on master

        Args:
            branch_name: str

        Returns:
            str
        """
        for commit in self.repo.iter_commits("origin/" + branch_name, reverse=True):
            if commit.hexsha not in self.master_shas:
                return commit.author.email

        raise ValueError(f"Didn't find author of branch {branch_name}")

    def localise_remote_branch(self, branch_name):
        """
        When new origin is added, we know nothing about remote branches.
        Make all remote branches available as local branches

        NOTE: Do not use to localise branches which are not main branch.
        Otherwise branches from other people will be localised and mess

        Args:
            branch_name: str

        Returns:
            None
        """
        self.repo.git.fetch()
        origin = self.repo.remotes.origin
        self.repo.create_head(
            branch_name, "origin/" + branch_name
        )  # create local branch "master" from remote "master"
        self.repo.heads.__getattr__(branch_name).set_tracking_branch(
            origin.refs.__getattr__(branch_name)
        )  # Set tracking information

    def remove_branch(self, branch_name):
        """
        Remove local branch

        Args:
            branch_name: str

        Returns:
            None
        """
        logger.info(f"Attempting to remove branch {branch_name}")
        branch_to_del = list(filter(lambda x: x.name == branch_name, self.repo.heads))
        assert (
            len(branch_to_del) == 1
        ), "Didn't found branch to delete or found too much"
        self.repo.delete_head(branch_to_del[0], force=True)
        logger.info(f"Branch removed {branch_name}")

    def remove_repo(self):
        """
        Remove current local repo

        Returns:
            None
        """
        logger.info(f"Attempting to remove repo {self.path}")
        rmtree(self.path)
        logger.info("Remove repo.")

    def reset_identical_commits(self):
        """
        Reset all commits with same name locally, so we can commit new name.
        There is no data loss here.

        Returns:
            bool, None
        """
        counter = 0
        for commit in self.repo.iter_commits():
            if commit.message.strip() == "Saved working set":
                counter = counter + 1
                continue

            break

        if counter > 0:
            self.repo.head.reset(f"HEAD~{counter}", index=False, working_tree=False)
        else:
            return False
