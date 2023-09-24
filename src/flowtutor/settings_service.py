import dbm
from os.path import join
from appdirs import user_config_dir
from pathlib import Path


class SettingsService:

    def set_setting(self, key: str, value: str) -> None:
        with dbm.open(join(user_config_dir('flowtutor'), 'settings.db'), 'c') as db:
            db[key] = str(value)

    def get_setting(self, key: str, default: str = '') -> str:
        Path(user_config_dir('flowtutor')).mkdir(parents=True, exist_ok=True)
        with dbm.open(join(user_config_dir('flowtutor'), 'settings.db'), 'c') as db:
            if key not in db:
                return default
            else:
                val = db[key].decode()
                return val if val else default
