import os
import yaml
from pathlib import Path
from zipfile import ZipFile


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent


def unzip_file(path):
    with ZipFile(path, 'r') as zipObj:
        zipObj.extractall(os.path.join(get_project_root(), 'tmp'))


def get_unpacked_repo_root(starting_pattern):
    for path in Path(os.path.join(get_project_root(), 'tmp')).glob(starting_pattern + '*'):
        return path.name, str(path.parent)


class Properties(object):
    # Virtual object to attach arguments
    pass


def get_git_providers():
    config_file = os.path.join(get_project_root(), 'git_providers.yaml')
    with open(config_file, 'r') as stream:
        config = yaml.safe_load(stream)
    return config


def get_config():
    config_file = os.path.join(get_project_root(), 'projects', 'config.yaml')
    if not os.path.exists(config_file):
        return False

    with open(config_file, 'r') as stream:
        config = yaml.safe_load(stream)

    return config


def set_config(config_dict):
    config_file = os.path.join(get_project_root(), 'projects', 'config.yaml')

    with open(config_file, 'w') as stream:
        yaml.dump(config_dict, stream)


def strip_string(string):
    return string.strip().lower().replace(' ',  '-')
