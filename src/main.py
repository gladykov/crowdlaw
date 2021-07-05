import gettext
import os

from controller.main_window import MainWindowCtrl
from controller.on_boarding import OnBoardingCtrl
from utils.utils import get_project_root


locale_dir = os.path.join(get_project_root(), "locale")

lang_en = gettext.translation("crowdlaw", localedir=locale_dir, languages=["en"])
lang_pl = gettext.translation("crowdlaw", localedir=locale_dir, languages=["pl"])
lang_en.install()


if __name__ == "__main__":

    on_boarding = True

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

        window = main_window.get_window("Code Law 1.0")

        if main_window.set_new_branch():  # Needed on first run after starting new proj
            window.close()
            window = main_window.get_window("Code Law 1.0")

        while True:
            event, values = window.read()
            print(event, "|", values)
            window = main_window.event_handler(window, event, values)

            if window is None:
                break
