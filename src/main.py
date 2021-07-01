import gettext
import os

import PySimpleGUI as sg
import yaml

from controller.main_window import MainWindowCtrl
from controller.on_boarding import OnBoardingCtrl
from UI.elements import Elements
from utils.utils import get_project_root

locale_dir = os.path.join(get_project_root(), "locale")

lang_en = gettext.translation('crowdlaw', localedir=locale_dir, languages=['en'])
lang_pl = gettext.translation('crowdlaw', localedir=locale_dir, languages=['pl'])
lang_en.install()


class Main:

    def __init__(self):
        config_file = "config.yaml"
        with open(config_file, 'r') as stream:
            config_file = yaml.safe_load(stream)

        # if not config_file["init"]:
        #     self.initiliase()
        # else:
        #     self.start_app()
        self.start_app()

    def start_app(self):
        app = Elements()
        app.layout()


if __name__ == "__main__":
    # Main()

    on_boarding = False

    if on_boarding:
        on_boarding = OnBoardingCtrl()
        window = on_boarding.get_window(_("On boarding"))

        while True:
            event, values = window.read()
            print(event, "|", values)
            window = on_boarding.event_handler(window, event, values)
            if window is None:
                break
            if window is True:
                on_boarding_success = True
                break

    on_boarding_success = True
    if on_boarding_success:
        main_window = MainWindowCtrl()
        window = main_window.get_window('Code Law 1.0')

        while True:
            event, values = window.read()
            print(event, "|", values)
            window = main_window.event_handler(window, event, values)

            if window is None:
                break
