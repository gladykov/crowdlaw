import gettext
import os
import yaml

from utils.utils import get_project_root
from UI.elements import Elements
import PySimpleGUI as sg

from controller.on_boarding import OnBoardingCtrl
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
    on_boarding = OnBoardingCtrl()
    window = on_boarding.draw_window(_("On boarding"))

    while True:
        event, values = window.read()
        print(event, "|", values)
        window = on_boarding.event_handler(window, event, values)
        if window is None:
            break
