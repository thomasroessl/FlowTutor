import dbm
from os.path import join
from appdirs import user_config_dir
from pathlib import Path


class SettingsService:
    '''Service for storing and retrieving settings between executions of FlowTutor.'''

    def set_setting(self, key: str, value: str) -> None:
        '''Saves a setting as a key value pair.

        Parameters:
            key (str): The identifier of the setting.
            value (str): The value of the setting.
        '''
        with dbm.open(join(user_config_dir('flowtutor'), 'settings.db'), 'c') as db:
            db[key] = str(value)

    def get_setting(self, key: str, default: str = '') -> str:
        '''Loads a setting from the setting store.

        Parameters:
            key (str): The identifier of the setting.
            default (str): The value that gets returned if the setting is not found with the key.
        '''
        Path(user_config_dir('flowtutor')).mkdir(parents=True, exist_ok=True)
        with dbm.open(join(user_config_dir('flowtutor'), 'settings.db'), 'c') as db:
            if key not in db:
                return default
            else:
                val = db[key].decode()
                return val if val else default
