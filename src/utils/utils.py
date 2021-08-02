import logging
import os
import re
from pathlib import Path
from zipfile import ZipFile


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


def get_token_name_token(url):
    # https://tokenname:MwJxgVNCdBcky6R@gitlab.com/gladykov/mynewnice.git
    parts = url.split(":")
    token_name = parts[1].split("//")[1]
    token = parts[2].split("@")[0]
    return token_name, token


def replace_string_between_subs(original, start_str, new_str, end_str):
    reg = "(?<=%s).*?(?=%s)" % (start_str, end_str)
    r = re.compile(reg, re.DOTALL)
    return r.sub(new_str, original)


def get_logger(name, propagate=False, log_level="info"):
    """

    Args:
        name: str
        propagate: bool - if logger entries should propagate up in the chain
        log_level: str - ex. info, debug

    Returns:
        logger
    """

    log_level = logging.DEBUG if log_level == "debug" else logging.INFO
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.propagate = propagate
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s", "%y/%m/%d %H:%M:%S"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
