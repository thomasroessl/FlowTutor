import dbm
from os import path
from appdirs import user_config_dir
from typing import Optional, Any
from pathlib import Path


class SettingsService:

    def set_setting(self, key: str, value: str) -> None:
        with dbm.open(path.join(user_config_dir('flowtutor'), 'settings.db'), 'c') as db:
            db[key] = str(value)

    def get_setting(self, key: str, default: Any) -> Optional[str]:
        Path(user_config_dir('flowtutor')).mkdir(parents=True, exist_ok=True)
        with dbm.open(path.join(user_config_dir('flowtutor'), 'settings.db'), 'c') as db:
            if key not in db:
                return str(default)
            else:
                return db[key].decode()
