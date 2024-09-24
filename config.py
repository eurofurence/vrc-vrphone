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
            "server_port": 9001,
            "microsip_binary": microsip_binary,
            "interaction_timeout": 3,
            "log_verbose": False,
            "phonebook":  [
                ["Lobby", "5229"],
                ["Lobby2", "5230"],
                ["Bark", "2275"],
                ["Conference", "1111"]
            ],
            "phonemenu": {
                "init_screen": "screensaver",
                "transition_popup": 3,
                "dialogs": {
                    "call_incoming":{
                        "dialog": 1,
                        "popup": 4,
                        "choices": {
                            "ok_button": ["call_accept", None],
                            "cancel_button": ["call_accept", None],
                            "yes_button": ["call_hangup", None],
                            "no_button": ["call_hangup", None]
                        }
                    },
                    "call_outgoing":{
                        "dialog": 2,
                        "popup": 1,
                        "choices": {
                            "yes_button": ["call_hangup", None],
                            "no_button": ["call_hangup", None]
                        }
                    },
                    "call_ended":{
                        "dialog": 3,
                        "popup": 0,
                        "choices": {}
                    },
                    "call_started":{
                        "dialog": 4,
                        "popup": 1,
                        "choices": {
                            "yes_button": ["call_hangup", None],
                            "no_button": ["call_hangup", None]
                        }
                    }
                },
                "screens": {
                    "screensaver": {
                        "screenid": 0,
                        "transition":  True,
                        "selectors": {
                            "selector1": False,
                            "selector2": False,
                            "selector3": False,
                            "selector4": False
                        },
                        "choices": {
                            "center_button": ["screen", "main"],
                            "keypad_button": ["screen", "main"],
                            "ok_button": ["screen", "main"],
                            "cancel_button": ["screen", "main"],
                            "yes_button": ["screen", "main"],
                            "no_button": ["screen", "main"]
                        }
                    },
                    "main": {
                        "screenid": 1,
                        "transition":  True,
                        "selectors": {
                            "selector1": True,
                            "selector2": False,
                            "selector3": True,
                            "selector4": True
                        },
                        "choices": {
                            "yes_button": ["screen", "credits"],
                            "no_button": ["screen", "secretmenu"],
                            "ok_button": ["screen", "phonebook"],
                            "cancel_button": ["screen", "conference"]
                        }
                    },
                    "phonebook": {
                        "screenid": 2,
                        "transition":  True,
                        "selectors": {
                            "selector1": True,
                            "selector2": True,
                            "selector3": True,
                            "selector4": True
                        },
                        "choices": {
                            "yes_button": ["call_phonebook", 0],
                            "no_button": ["call_phonebook", 1],
                            "ok_button": ["call_phonebook", 2],
                            "cancel_button": ["screen", "main"]
                        }
                    },
                    "conference": {
                        "screenid": 3,
                        "transition":  True,
                        "selectors": {
                            "selector1": False,
                            "selector2": False,
                            "selector3": True,
                            "selector4": True
                        },
                        "choices": {
                            "ok_button": ["call_phonebook", 3],
                            "cancel_button": ["screen", "main"]
                        }
                    },
                    "credits": {
                        "screenid": 4,
                        "transition":  True,
                        "selectors": {
                            "selector1": False,
                            "selector2": False,
                            "selector3": False,
                            "selector4": True
                        },
                        "choices": {
                            "cancel_button": ["screen", "main"]
                        }
                    },
                    "secretmenu": {
                        "screenid": 5,
                        "transition":  True,
                        "selectors": {
                            "selector1": False,
                            "selector2": False,
                            "selector3": False,
                            "selector4": True
                        },
                        "choices": {
                            "cancel_button": ["screen", "main"]
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
