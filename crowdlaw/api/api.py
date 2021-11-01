"""Synthetic module to get proper Git API"""
from crowdlaw.api.gitlab_api import GitlabAPI


def get_api(api, git_providers):
    """
    For future, when more than one API will be supported.
    :param api: str
    :param git_providers: lst
    :return: object
    """
    if api not in list(git_providers.keys()):
        raise ValueError(_("Unsupported API provided: {api}").format(api=api))

    if api == "gitlab":
        return GitlabAPI
