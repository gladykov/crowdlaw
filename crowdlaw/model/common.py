"""Module with model helpers"""
import os
import webbrowser

import requests
import yaml

from crowdlaw.utils.utils import get_project_root, get_projects_path


class BaseModel:
    """BaseModel class with various helpers"""

    def __init__(self):
        self.theme = "DarkTeal6"

    @staticmethod
    def git_providers():
        """
        Get supported Git providers and their params

        Returns:
            dict
        """
        config_file = os.path.join(
            get_project_root(), "resources", "git_providers.yaml"
        )
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
        config_file = os.path.join(get_projects_path(), "config.yaml")
        if not os.path.exists(config_file):
            return False

        with open(config_file, "r") as stream:
            config = yaml.safe_load(stream)

        return config

    @staticmethod
    def set_config(config_dict):
        """
        Write config to a file

        Args:
            config_dict: dict

        Returns:
            None
        """
        config_file_dir = os.path.join(get_projects_path())
        config_file = "config.yaml"
        config_file_path = os.path.join(config_file_dir, config_file)
        if not os.path.exists(config_file_dir):
            os.makedirs(config_file_dir)
        with open(config_file_path, "w") as stream:
            yaml.dump(config_dict, stream)

    @staticmethod
    def open_url_in_browser(url):
        """
        Open URL in Web browser

        Args:
            url: str

        Returns:
            None
        """
        webbrowser.open(url)

    @staticmethod
    def get_file_from_url(url):
        """
        Get text content of file from URL

        Args:
            url: str

        Returns:
            str: text content of file
        """
        request = requests.get(url)
        return request.text if request.status_code == 200 else None

    @staticmethod
    def get_version():
        """
        Get app version from local file

        Returns:
            str
        """
        with open(
            os.path.join(get_project_root(), "resources", "VERSION"), "r"
        ) as file:
            return file.readline()
