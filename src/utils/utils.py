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


def strip_string(string):
    return string.strip().lower().replace(" ", "-")
