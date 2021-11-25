"""Main entry program of Crowd Law"""
import locale
from sys import exit

from crowdlaw.controller.language import LanguageCtrl
from crowdlaw.controller.main_window import MainWindowCtrl
from crowdlaw.controller.on_boarding import OnBoardingCtrl
from crowdlaw.model.common import BaseModel
from crowdlaw.utils.supported_langs import get_language_name_by_shortcut
from crowdlaw.utils.utils import get_logger, redirect_stderr_to_logger


logger = get_logger("root", log_level="debug")
redirect_stderr_to_logger(logger)


def main():
    """Main entry point"""
    logger.info(f"Starting Crowd Law app version {BaseModel.get_version()}")
    initialized = bool(BaseModel.get_config())

    if not initialized:
        # Autodetect local language
        local_lang = locale.getdefaultlocale()[0]
        if get_language_name_by_shortcut(local_lang, False) is False:
            # Default to default
            local_lang = "en_US"

        config = {"lang": local_lang, "init": False}
        BaseModel.set_config(config)

    LanguageCtrl.install_lang()

    if BaseModel.get_config()["init"] is True:
        on_boarding_success = True
    else:
        on_boarding_success = False
        logger.info("Starting on boarding flow.")
        on_boarding = OnBoardingCtrl()
        window = on_boarding.get_window(_("On boarding"))

        while True:
            event, values = window.read()
            if None in [event, values]:
                break
            logger.debug(str(event) + " | " + str(values))
            window = on_boarding.event_handler(window, event, values)
            if window is None:
                break
            if window is True:
                on_boarding_success = True
                break

    if on_boarding_success:
        logger.info("Initializing main window.")
        main_window = MainWindowCtrl()
        if main_window.model.remote_api.connected:
            if not main_window.model.remote_api.authenticated:
                # Need to update token
                main_window.update_token_info()

        window = main_window.get_window(main_window.model.app_title)

        if main_window.set_new_branch():  # Needed on first run after starting new proj
            window.close()
            window = main_window.get_window(main_window.model.app_title)

        while True:
            event, values = window.read()
            logger.debug(str(event) + "|" + str(values))
            window = main_window.event_handler(window, event, values)

            if window is None:
                logger.info("No main window anymore.")
                break

        logger.info("Bye bye")
        exit()

    logger.warning("On boarding did not succeed")
    exit()


if __name__ == "__main__":
    main()
