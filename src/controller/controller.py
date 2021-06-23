import PySimpleGUI as sg
import os.path
import yaml

from src.UI.elements import Elements
from src.api.api import get_api
from src.git_adapter.git_adapter import GitAdapter

config_file = '../config.yaml'


class Controller:

    def __init__(self):
        self.config_file = config_file
        self.elements = Elements()
        # Do not get API before we are initialized
        self.api = get_api("gitlab")
        # No need to nilize git aapter if path is uknown
        # self.git_adapter = GitAdapter()
        self.initialized = self.is_initialized()

    def main(self):
        if not self.initialized:
            self.initialize()

    def is_initialized(self):
        if not os.path.isfile(self.config_file):
            return False

        with open(self.config_file, 'r') as stream:
            config = yaml.safe_load(stream)

        return config["initialized"] == 1

    def initialize(self):
        onboarding_window = self.elements.on_boarding()
        while True:
            event, values = onboarding_window.read()
            print(event, "|", values)
            if event in ["Close", sg.WIN_CLOSED]:
                onboarding_window.close()
                exit("App closed. Bye!")
