import os
import webbrowser

import yaml

from src.utils.utils import get_project_root


class Base:
    """Base class with various helpers"""

    @staticmethod
    def git_providers():
        """
        Get supported Git providers and their params

        Returns:
            dict
        """
        config_file = os.path.join(get_project_root(), "git_providers.yaml")
        with open(config_file, "r") as stream:
            config = yaml.safe_load(stream)
        return config

    @staticmethod
    def get_config():
        """
        Get local config file, with projects and more

        Returns:
            dict
        """
        config_file = os.path.join(get_project_root(), "projects", "config.yaml")
        if not os.path.exists(config_file):
            return False

        with open(config_file, "r") as stream:
            config = yaml.safe_load(stream)

        return config

    @staticmethod
    def get_stages(project_name):
        """
        Get stages for current project and their state

        Args:
            project_name: str

        Returns:
            dict
        """
        stages_file = os.path.join(
            get_project_root(), "projects", project_name, "stages.yaml"
        )
        if not os.path.exists(stages_file):
            raise EnvironmentError("Couldn't find valid stages.yaml file")

        with open(stages_file, "r") as stream:
            stages = yaml.safe_load(stream)

        return stages

    @staticmethod
    def set_config(config_dict):
        """
        Write config to a file

        Args:
            config_dict: dict

        Returns:
            None
        """
        config_file = os.path.join(get_project_root(), "projects", "config.yaml")

        with open(config_file, "w") as stream:
            yaml.dump(config_dict, stream)

    @staticmethod
    def open_url_in_browser(url):
        """
        Open URL in Webbrowser

        Args:
            url: str

        Returns:
            None
        """
        webbrowser.open(url)
