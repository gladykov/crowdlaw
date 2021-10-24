"""Utils and helpers"""
import logging
import re
from pathlib import Path


def get_project_root() -> Path:
    """
    Get project root

    Returns:
        path, str
    """
    return Path(__file__).parent.parent.parent


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
    ch.setLevel(log_level)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s", "%y/%m/%d %H:%M:%S"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


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
