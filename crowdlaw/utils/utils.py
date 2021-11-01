"""Utils and helpers"""
import io
import logging
import os
import re
import sys
from pathlib import Path


def get_project_root() -> Path:
    """
    Get project root

    Returns:
        path, str
    """
    return Path(__file__).parent.parent


def get_home_user_path():
    """Folder where user files are written. Create it, if there is none."""
    home_user_path = os.path.join(Path.home(), ".crowdlaw")
    if not os.path.isdir(home_user_path):
        os.makedirs(home_user_path)
    return home_user_path


def get_projects_path():
    """Path were projects are stored"""
    return os.path.join(get_home_user_path(), "projects")


def strip_string(string):
    """
    Remove white spaces and replace spaces with -
    Args:
        string: str

    Returns:
        str
    """
    return string.strip().lower().replace(" ", "-")


def get_token_name_token(url):
    """
    Get token name and token from URLs in Git config files
    Args:
        url:

    Returns:
        tuple (token_name, token)
    """
    # https://tokenname:MwJxgVNCdBcky6R@gitlab.com/gladykov/mynewnice.git
    parts = url.split(":")
    token_name = parts[1].split("//")[1]
    token = parts[2].split("@")[0]
    return token_name, token


def replace_string_between_subs(original, start_str, new_str, end_str):
    """
    Replace string between start and end

    Args:
        original: string
        start_str: start pattern to be found
        new_str: replacement part
        end_str: end pattern to be found

    Returns:
        string
    """
    reg = "(?<=%s).*?(?=%s)" % (start_str, end_str)
    r = re.compile(reg, re.DOTALL)
    return r.sub(new_str, original)


def get_logger(name, propagate=False, log_level="info"):
    """
    Get logger

    Args:
        name: str
        propagate: bool - if logger entries should propagate up in the chain
        log_level: str - ex. info, debug

    Returns:
        logger
    """

    logger = logging.getLogger(name)
    if logger.hasHandlers():  # Already exists
        return logger

    log_level = logging.DEBUG if log_level == "debug" else logging.INFO
    logger.setLevel(log_level)
    logger.propagate = propagate

    ch = logging.StreamHandler()
    log_file = os.path.join(get_home_user_path(), "crowdlaw.log")
    fh = logging.FileHandler(log_file, "a", "utf-8")

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s", "%y/%m/%d %H:%M:%S"
    )

    for handler in [ch, fh]:
        handler.setLevel(log_level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def redirect_stderr_to_logger(logger):
    """One to rule them all"""

    class MyStream(io.IOBase):
        """Class to reroute stderr to logger"""

        def __init__(self, logger):
            self.logger = logger

        def write(self, s):
            """Write"""
            s = s.strip()
            if s != "":
                self.logger.error(s)

    sys.stderr = MyStream(logger)


def urljoin(parts):
    """
    os.path.join but for URLs

    Args:
        parts: list

    Returns:
        str
    """
    # https://stackoverflow.com/a/63678718
    return "/".join(parts).replace("//", "/").replace(":/", "://")


def super_init(func):
    """
    Wrapper, to trigger super __init__, if init is simple enough
    https://stackoverflow.com/questions/3782827/why-arent-superclass-init-methods-automatically-invoked

    Args:
        func: method

    Returns:
        wrapper
    """

    def wrapper(self, *args, **kwargs) -> None:
        """
        Trigger __init__
        Args:
            self:
            *args:
            **kwargs:

        Returns:
            None
        """
        super(type(self), self).__init__(*args, **kwargs)
        func(self)

    return wrapper
