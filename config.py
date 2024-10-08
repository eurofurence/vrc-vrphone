import json
import os

def merge_dicts(dict1, dict2):
    """ Recursively merges dict2 into dict1 """
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return dict2
    for k in dict2:
        if k in dict1:
            dict1[k] = merge_dicts(dict1[k], dict2[k])
        else:
            dict1[k] = dict2[k]
    return dict1

class Config:
    def __init__(self):
        appdata_path = os.environ.get('LOCALAPPDATA')
        microsip_binary = os.path.join(appdata_path, "MicroSIP\\microsip.exe")
        self.APP_NAME = 'VRChatVRPhone'
        self.default_config = {
            "version": 1,
            "server_port": 9001,
            "microsip_binary": microsip_binary,
            "interaction_timeout": 3,
            "log_verbose": False,
            "phonebook":  [
                ["Entry1", "5229"],
                ["Entry2", "5230"],
                ["Entry3", "2275"],
                ["Conference", "1111"]
            ],
            "phonemenu": {
                "init_screen": "main",
                "transition_popup": 1,
                "dialogs": {
                    "call_incoming":{
                        "dialog": 1,
                        "window": 2,
                        "popup": 0,
                        "numbers": {
                            "row1": "callerid",
                            "row2": None
                        },
                        "choices": {
                            "yes_button": ["call_accept", None],
                            "no_button": ["call_hangup", None]
                        }
                    },
                    "call_outgoing":{
                        "dialog": 2,
                        "window": 2,
                        "popup": 0,
                        "numbers": {
                            "row1": "callerid",
                            "row2": None
                        },
                        "choices": {
                            "no_button": ["call_hangup", None]
                        }
                    },
                    "call_confirm":{
                        "dialog": 3,
                        "window": 2,
                        "popup": 0,
                        "numbers": {
                            "row1": "phonebook",
                            "row2": None
                        },
                        "choices": {
                            "yes_button": ["phonebook_call_active_entry", None],
                            "no_button": ["exit_dialogs", None]
                        }
                    },
                    "call_end":{
                        "dialog": 5,
                        "window": 2,
                        "popup": 0,
                        "numbers": {
                            "row1": "callerid",
                            "row2": "calltimer"
                        },
                        "choices": {}
                    },
                    "call_start":{
                        "dialog": 4,
                        "window": 2,
                        "popup": 0,
                        "numbers": {
                            "row1": "callerid",
                            "row2": "calltimer"
                        },
                        "choices": {
                            "no_button": ["call_hangup", None]
                        }
                    }
                },
                "screens": {
                    "main": {
                        "screenid": 1,
                        "window": 0,
                        "popup": 0,
                        "numbers": {
                            "row1": None,
                            "row2": "systemtime"
                        },
                        "selectors": {},
                        "choices": {
                            "yes_button": ["screen", "phonebook"]
                        }
                    },
                    "phonebook": {
                        "screenid": 2,
                        "window": 0,
                        "popup": 0,
                        "numbers": {
                            "row1": "phonebook",
                            "row2": "entry"
                        },
                        "selectors": {},
                        "choices": {
                            "yes_button": ["dialog", "call_confirm"],
                            "no_button": ["screen", "main"],
                            "ok_button": ["phonebook_switch", "next"],
                            "cancel_button": ["phonebook_switch", "prev"]
                        }
                    }
                }
            }
        }
        self.current_config = None

    def get_by_key(self, key: str):
        return self.current_config.get(key)

    def update(self, key: str, nextValue):
        if (key in self.current_config):
            self.current_config[key] = nextValue

    def read_config_from_disk(self):
        appdata_path = os.environ.get('LOCALAPPDATA')
        app_directory = os.path.join(appdata_path, self.APP_NAME)
        os.makedirs(app_directory, exist_ok=True)
        config_path = os.path.join(app_directory, 'config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as file:
                data = json.load(file)
                data = merge_dicts(self.default_config, data)
                return data
        else:
            with open(config_path, 'w') as file:
                json.dump(self.default_config, file, indent=4)
            return self.default_config

    def write_config_to_disk(self):
        if self.current_config == None:
            return
        appdata_path = os.environ.get('LOCALAPPDATA')
        app_directory = os.path.join(appdata_path, self.APP_NAME)
        os.makedirs(app_directory, exist_ok=True)
        config_path = os.path.join(app_directory, 'config.json')
        with open(config_path, 'w') as file:
            json.dump(self.current_config, file, indent=4)

    def init(self):
        self.current_config = self.read_config_from_disk()
