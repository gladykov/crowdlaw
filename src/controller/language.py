import gettext
import locale
import os
import platform

from src.model.base import Base
from src.utils.supported_langs import set_keyboard_language, supported_langs
from src.utils.utils import get_logger, get_project_root


logger = get_logger("root", log_level="debug")


class LanguageCtrl:
    @staticmethod
    def install_lang():
        locale_dir = os.path.join(get_project_root(), "locale")
        lang_code = LanguageCtrl.get_app_lang()
        lang_2_chars = lang_code.split("_")[0]
        logger.debug(f"Detected lang to be used {lang_2_chars}")
        lang = gettext.translation(
            "crowdlaw", localedir=locale_dir, languages=[lang_2_chars]
        )
        lang.install()
        if platform.system() == "Windows":
            set_keyboard_language(lang_code)

    @staticmethod
    def get_app_lang():
        config = Base.get_config()
        if config["lang"] == "None":  # First time run
            current_locale = locale.getdefaultlocale()[0]  # ('pl_PL', 'cp1252')
            print(f"Detected system language as {current_locale}")
            for supported_locale_dict in supported_langs.values():
                if supported_locale_dict["shortcut"] == current_locale:
                    use_lang_shortcut = supported_locale_dict["shortcut"]

                    config["lang"] = use_lang_shortcut
                    Base.set_config(config)
                    return use_lang_shortcut

            # Default to English
            config["lang"] = "en_US"
            Base.set_config(config)
            return config["lang"]

        else:
            return config["lang"]

    @staticmethod
    def set_app_lang(lang_shortcut):
        config = Base.get_config()
        config["lang"] = lang_shortcut
        Base.set_config(config)

    @staticmethod
    def supported_langs():
        """
        Get supported languages
        """
        return list(supported_langs.keys())

    @staticmethod
    def switch_app_lang(lang):
        lang_shortcut = supported_langs[lang]["shortcut"]
        LanguageCtrl.set_app_lang(lang_shortcut)
        LanguageCtrl.install_lang()
