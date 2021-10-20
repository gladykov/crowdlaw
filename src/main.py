# -*- coding: utf8 -*-
import PySimpleGUI as sg

from controller.main_window import MainWindowCtrl
from controller.on_boarding import OnBoardingCtrl
from src.controller.language import LanguageCtrl
from utils.utils import get_logger
from src.model.base import Base
from src.views.common import select_language


logger = get_logger("root", log_level="debug")


if __name__ == "__main__":
    logger.info("Starting Crowd Law app version 1.0")
    initialized = False
    initialized = bool(Base.get_config())

    if not initialized:
        language_selector = select_language()
        print(language_selector)
        if language_selector[0] != "OK":
            exit("Didn't choose valid language. Bye bye!")

        selected_lang = None
        for lang, val in language_selector[1].items():
            if val is True:
                selected_lang = lang
                break

        if selected_lang is None:
            exit("Didn't choose valid language. Bye bye!")

        print(selected_lang)
        config = {"lang": selected_lang, "init": False}
        Base.set_config(config)

    LanguageCtrl.install_lang()

    if Base.get_config()["init"] is True:
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
            logger.debug(event + " | " + str(values))
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
            print(event, "|", values)
            window = main_window.event_handler(window, event, values)
            # Close any animated popup window
            sg.popup_animated(None)

            if window is None:
                logger.info("No main window anymore.")
                break

        logger.info("Bye bye")
        exit()

    logger.warning("On boarding did not succeed")
    exit()
