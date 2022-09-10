from ast import literal_eval
from typing import Dict, Union


class Settings:

    settings: Dict[str, Union[str, int, float, bool]] = {}

    @staticmethod
    def set_setting(key: str, value: Union[str, int, float, bool]):
        Settings.settings[key] = value
        with open("flowtutor_settings", "w") as file:
            file.write(str(Settings.settings))

    @staticmethod
    def get_setting(key: str, default: Union[str, int, float, bool]) -> Union[str, int, float, bool]:
        if len(Settings.settings) == 0:
            with open("flowtutor_settings", "r") as file:
                content = file.read()
                if len(content) > 0:
                    Settings.settings = literal_eval(content)
        return Settings.settings.get(key, default)
