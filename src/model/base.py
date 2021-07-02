import os
import yaml
from src.utils.utils import get_project_root
import webbrowser


class Base:
    @staticmethod
    def git_providers():
        config_file = os.path.join(get_project_root(), "git_providers.yaml")
        with open(config_file, "r") as stream:
            config = yaml.safe_load(stream)
        return config

    @staticmethod
    def get_config():
        config_file = os.path.join(get_project_root(), "projects", "config.yaml")
        if not os.path.exists(config_file):
            return False

        with open(config_file, "r") as stream:
            config = yaml.safe_load(stream)

        return config

    @staticmethod
    def set_config(config_dict):
        config_file = os.path.join(get_project_root(), "projects", "config.yaml")

        with open(config_file, "w") as stream:
            yaml.dump(config_dict, stream)

    @staticmethod
    def open_url_in_browser(url):
        webbrowser.open(url)
