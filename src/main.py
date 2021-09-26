# -*- coding: utf8 -*-
import PySimpleGUI as sg

from controller.main_window import MainWindowCtrl
from controller.on_boarding import OnBoardingCtrl
from src.controller.language import LanguageCtrl
from utils.utils import get_logger


logger = get_logger("root", log_level="debug")


if __name__ == "__main__":
    LanguageCtrl.install_lang()
    logger.info("Starting Crowd Law app version 1.0")

    on_boarding = False

    if on_boarding:
        logger.info("Starting on boarding flow.")
        on_boarding = OnBoardingCtrl()
        window = on_boarding.get_window(_("On boarding"))

        while True:
            event, values = window.read()
            logger.debug(event, "|", values)
            window = on_boarding.event_handler(window, event, values)
            if window is None:
                break
            if window is True:
                on_boarding_success = True
                break

    on_boarding_success = True
    if on_boarding_success:
        logger.info("Initializing main window.")
        main_window = MainWindowCtrl()
        if not main_window.model.remote_api.authenticated:
            # Need to update token
            main_window.update_token_info()

        window = main_window.get_window("Code Law 1.0")

        if main_window.set_new_branch():  # Needed on first run after starting new proj
            window.close()
            window = main_window.get_window("Code Law 1.0")

        while True:
            event, values = window.read()
            logger.debug(event, "|", values)
            window = main_window.event_handler(window, event, values)
            # Close any animated popup window
            sg.popup_animated(None)

            if window is None:
                logger.info("No main window anymore.")
                break

        logger.info("Bye bye")
        exit()
