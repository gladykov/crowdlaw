import os
from pathlib import Path
from zipfile import ZipFile

import yaml


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent


def unzip_file(path):
    with ZipFile(path, "r") as zipObj:
        zipObj.extractall(os.path.join(get_project_root(), "tmp"))


def get_unpacked_repo_root(starting_pattern):
    for path in Path(os.path.join(get_project_root(), "tmp")).glob(
        starting_pattern + "*"
    ):
        return path.name, str(path.parent)


class PropertiesOnboarding:
    def __init__(self):
        self.new_existing = None
        self.project_url = None
        self.project_name = None
        self.git_provider = None
        self.username = None
        self.token = None
        self.token_name = None
        self.theme = "Dashboard"  # Move to some common CTRL
        self.supported_git_providers = list(get_git_providers().keys())


class PropertiesMainWindow:
    def __init__(self):
        self.edited_file = None
        self.new_existing = None
        self.project_url = None
        self.project_name = None
        self.git_provider = None
        self.username = None
        self.token = None
        self.token_name = None
        self.theme = "Dashboard"  # Move to some common CTRL
        self.supported_git_providers = list(get_git_providers().keys())
        self.editor_disabled = True


def get_git_providers():
    config_file = os.path.join(get_project_root(), "git_providers.yaml")
    with open(config_file, "r") as stream:
        config = yaml.safe_load(stream)
    return config


def get_config():
    config_file = os.path.join(get_project_root(), "projects", "config.yaml")
    if not os.path.exists(config_file):
        return False

    with open(config_file, "r") as stream:
        config = yaml.safe_load(stream)

    return config


def set_config(config_dict):
    config_file = os.path.join(get_project_root(), "projects", "config.yaml")

    with open(config_file, "w") as stream:
        yaml.dump(config_dict, stream)


def strip_string(string):
    return string.strip().lower().replace(" ", "-")
