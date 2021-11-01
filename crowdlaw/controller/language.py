"""Language support module"""
import gettext
import locale
import os
import platform

from crowdlaw.model.common import BaseModel
from crowdlaw.utils.supported_langs import set_keyboard_language, supported_langs
from crowdlaw.utils.utils import get_logger, get_project_root


logger = get_logger("root", log_level="debug")


class LanguageCtrl:
    """Language methods"""

    @staticmethod
    def install_lang():
        """
        Enable language and correct keyboard layout

        Returns:
            None
        """
        locale_dir = os.path.join(get_project_root(), "locale")
        lang_code = LanguageCtrl.get_app_lang()
        logger.debug(f"Detected lang to be used {lang_code}")
        lang = gettext.translation(
            "crowdlaw", localedir=locale_dir, languages=[lang_code]
        )
        lang.install()
        if platform.system() == "Windows":
            set_keyboard_language(lang_code)

    @staticmethod
    def get_app_lang():
        """
        Detect which language should be used

        Returns:
            str, ex. 'en_US'
        """
        config = BaseModel.get_config()
        if config["lang"] == "None":  # First time run
            current_locale = locale.getdefaultlocale()[0]  # ('pl_PL', 'cp1252')
            logger.debug(f"Detected system language as {current_locale}")
            for supported_locale_dict in supported_langs.values():
                if supported_locale_dict["shortcut"] == current_locale:
                    use_lang_shortcut = supported_locale_dict["shortcut"]

                    config["lang"] = use_lang_shortcut
                    BaseModel.set_config(config)

            # Default to English
            config["lang"] = "en_US"
            BaseModel.set_config(config)

        return config["lang"]

    @staticmethod
    def set_app_lang(lang_shortcut):
        """
        Write which language should be used to config

        Args:
            lang_shortcut: str

        Returns:
            None
        """
        config = BaseModel.get_config()
        config["lang"] = lang_shortcut
        BaseModel.set_config(config)

    @staticmethod
    def supported_langs():
        """
        Get supported languages

        Returns:
            list
        """
        return list(supported_langs.keys())

    @staticmethod
    def switch_app_lang(lang):
        """
        Switch application language

        Args:
            lang: str

        Returns:
            None
        """
        lang_shortcut = supported_langs[lang]["shortcut"]
        LanguageCtrl.set_app_lang(lang_shortcut)
        LanguageCtrl.install_lang()
