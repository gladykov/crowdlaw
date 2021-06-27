import os.path
import webbrowser

import PySimpleGUI as sg
import validators

from src.api.api import get_api
from src.controller.common import CommonCtrl, file_icon, folder_icon
from src.git_adapter.git_adapter import GitAdapter
from src.utils.utils import (PropertiesMainWindow, PropertiesOnboarding,
                             get_config, get_git_providers, get_project_root,
                             set_config, strip_string)
from src.views.common import warning_popup
from src.views.main_window import MainWindowUI


class MainWindowCtrl(CommonCtrl):

    def __init__(self):
        self.props = PropertiesMainWindow()
        self.config = get_config()
        self.props.project_name = self.config['last_project']
        self.props.project_url = self.config['projects'][self.props.project_name]['repo']['url']
        self.props.username = self.config['projects'][self.props.project_name]['repo']['user']
        self.props.list_of_files = self.get_treedata(os.path.join(get_project_root(), 'projects', 'monopipeline'))

    def get_treedata(self, starting_path):
        treedata = sg.TreeData()

        def add_files_in_folder(parent, dirname):
            files = os.listdir(dirname)
            for f in files:
                fullname = os.path.join(dirname, f)
                if os.path.isdir(fullname):  # if it's a folder, add folder and recurse
                    treedata.Insert(parent, fullname, f, values=[], icon=folder_icon)
                    add_files_in_folder(fullname, fullname)
                else:

                    treedata.Insert(parent, fullname, f, values=[
                        os.stat(fullname).st_size], icon=file_icon)

        add_files_in_folder('', starting_path)

        return treedata



    def read_list_of_files(self, folder):
        reedata = sg.TreeData()
    def add_files_in_folder(parent, dirname):
        files = os.listdir(dirname)
        for f in files:
            fullname = os.path.join(dirname, f)
            if os.path.isdir(fullname):  # if it's a folder, add folder and recurse
                treedata.Insert(parent, fullname, f, values=[], icon=folder_icon)
                add_files_in_folder(fullname, fullname)
            else:

                treedata.Insert(parent, fullname, f, values=[
                    os.stat(fullname).st_size], icon=file_icon)

    def get_elements(self):
        return MainWindowUI(self.props).layout()

    def get_window(self, window_title, location=(None, None)):
        return self.draw_window(window_title, self.get_elements(), location)
