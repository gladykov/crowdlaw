import os.path
import webbrowser

import PySimpleGUI as sg
import validators

from src.api.api import get_api
from src.controller.common import CommonCtrl
from src.git_adapter.git_adapter import GitAdapter
from src.utils.utils import (PropertiesOnboarding, get_config,
                             get_git_providers, get_project_root, set_config,
                             strip_string)
from src.views.common import warning_popup
from src.views.on_boarding import OnBoardingUI


class OnBoardingCtrl(CommonCtrl):

    def __init__(self):
        self.props = PropertiesOnboarding()
        self.page = 1

    def get_elements(self):
        if self.page == 1:
            return OnBoardingUI(self.props).select_project_intention()
        else:
            return OnBoardingUI(self.props).git_details()

    def get_window(self, window_title, location=(None, None)):
        return self.draw_window(window_title, self.get_elements(), location)

    def validate_page_1(self, values):
        issues = []
        if not values['new'] and not values['existing']:
            issues.append(_("Please select if you want to join new or existing project"))
        if values['new'] and not values['project_name']:
            issues.append(_("Provide project name"))
        if values['existing'] and not values['project_url']:
            issues.append(_("Provide project URL"))
        if values['existing'] and values['project_url']:
            if validators.url(values['project_url']):
                found = False
                for provider in self.props.supported_git_providers:
                    if provider in values['project_url']:
                        found = True
                        self.props.git_provider = provider
                        break
                if not found:
                    issues.append(_("Provided unsupported website URL"))
            else:
                issues.append(_("Provide valid project URL"))
        if issues:
            warning_popup(issues)
            return False
        else:
            return True

    def collect_page_1(self, values):
        if values['new']:
            self.props.project_name = values['project_name']
        else:
            self.props.project_url = values['project_url']
            self.props.project_name = values['project_url'].split('/')[-1].split('.')[0]
            print(self.props.project_name)

    def validate_page_2(self, values):
        issues = []
        if not values['username_input']:
            issues.append(_("Provide username"))
        if not values['token_input']:
            issues.append(_("Provide API token key"))
        if not values['token_name_input']:
            issues.append(_("Provide API token key name"))

        if issues:
            warning_popup(issues)
            return False
        else:
            return True

    def collect_page_2(self, values):
        self.props.username = values['username_input']
        self.props.token = values['token_input']
        self.props.token_name = values['token_name_input']
        self.props.git_provider = values['git_provider']

    def initialize_project(self):
        new_project = self.props.new_existing == 'new'
        project_stripped_name = strip_string(self.props.project_name)

        if new_project:
            self.props.project_url = '/'.join([
                get_git_providers()[self.props.git_provider]['base_url'],
                self.props.username,
                project_stripped_name
            ])

        config = get_config()

        if config and self.props.project_name in config['projects'].keys():
            warning_popup([_(f"Project {self.props.project_name} already exists")])
            return False

        project_dir = os.path.join(get_project_root(), 'projects', project_stripped_name)

        if not os.path.exists(project_dir):
            os.mkdir(project_dir)
        else:
            warning_popup([_(f"Project folder {project_dir} already exists")])
            return False

        RemoteAPI = get_api(self.props.git_provider)
        remote_api = RemoteAPI(self.props.username, self.props.token)

        if new_project:
            project = remote_api.get_project_info(remote_api.create_empty_project(self.props.project_name))
        else:
            project_details = self.props.project_url.split('/')
            project_to_fork = remote_api.get_project_by_user_path(project_details[-2], project_details[-1])
            forked_proj = remote_api.fork_project(project_to_fork)
            project = remote_api.get_project_info(forked_proj)

        username = project['username']
        user_name = project['user_name']
        email = project['email']
        repo_name = project['repo_name']
        repo_git_url = project['repo_git_url']
        repo_web_url = project['repo_web_url']
        path = project['path']

        git_adapter = GitAdapter(project_dir, initialized=False)
        git_adapter.set_config('user', 'name', user_name)
        git_adapter.set_config('user', 'email', email)
        repo_git_url = remote_api.get_credentials_git_url(self.props.token_name, path)
        git_adapter.set_config('remote "origin"', 'url', repo_git_url)

        if new_project:
            for example_file in ['example_1.txt', 'example_2.txt', 'example_3.txt']:
                with open(os.path.join(project_dir, example_file), 'w') as fp:
                    fp.write(_(f"Contents of {example_file}"))

            git_adapter.add_all_untracked()
            git_adapter.commit(_(f"Initial commit for project {self.props.project_name}"))
            git_adapter.push()
        else:
            git_adapter.pull()

        # And now we can write config
        project_dict = {
            'nice_name': repo_name,
            'provider': self.props.git_provider,
            'username': username,
            'project_url': repo_web_url,
            'is_owner': new_project,
            'folder': project_dir,
        }

        if not config:
            config = {
                'init': True,
                'projects': {},
                'lang': 'en',  # TODO: Set and Get current language during on boarding
            }

        config['projects'][self.props.project_name] = project_dict
        config['last_project'] = self.props.project_name

        set_config(config)
        return True

    def event_handler(self, window, event, values):
        if event == 'new':
            self.props.new_existing = event
            new_window = self.get_window('updated', window.CurrentLocation())
            window.close()
            return new_window
        if event == 'existing':
            self.props.new_existing = event
            new_window = self.get_window('existing', window.CurrentLocation())
            window.close()
            return new_window

        if event == 'next':
            if self.validate_page_1(values):
                self.collect_page_1(values)
                self.page = 2
                new_window = self.get_window('git details title', window.CurrentLocation())
                window.close()
                return new_window

        if event == "back":
            self.page = 1
            self.collect_page_2(values)
            new_window = self.get_window('git details title', window.CurrentLocation())
            window.close()
            return new_window

        if event == 'git_provider':
            self.props.git_provider = values[event]
            self.collect_page_2(values)
            new_window = self.get_window('git details changed', window.CurrentLocation())
            window.close()
            return new_window

        if event == 'create_account':
            webbrowser.open(
                get_git_providers()[self.props.git_provider]['base_url'] +
                get_git_providers()[self.props.git_provider]['create_account']
            )

        if event == 'obtain_token':
            webbrowser.open(
                get_git_providers()[self.props.git_provider]['base_url'] +
                get_git_providers()[self.props.git_provider]['get_token']
            )

        if event == "start":
            if self.validate_page_2(values):
                self.collect_page_2(values)
                if self.initialize_project():
                    return True

        if event in ["close", sg.WIN_CLOSED]:
            window.close()
            return None

        return window
