from src.api.gitlab_api import GitlabAPI
from src.utils.utils import get_git_providers


def get_api(api):
    if api not in list(get_git_providers().keys()):
        raise ValueError(_(f"Unsupported API provided: {api}"))

    if api == 'gitlab':
        return GitlabAPI
