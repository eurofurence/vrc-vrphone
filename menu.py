from config import Config
from gui import Gui
import json
import params
import os

class Menu:
    def  __init__(self, config: Config, gui: Gui, main_queue: set = set(), output_queue: set = set()):
        self.config = config
        self.gui = gui
        self.main_queue = main_queue
        self.output_queue = output_queue
        self.active_screen = None
        self.active_dialog = 0
        self.active_popup = 0
        self.menu_osc_int_parameter_map: dict[str, str] = {
            "screen": params.show_screen,
            "dialog": params.show_dialog,
            "popup": params.show_popup
        }
        self.menu_osc_bool_parameter_map: dict[str, str] = {
            "selector1": params.show_selection1,
            "selector2": params.show_selection2,
            "selector3": params.show_selection3,
            "selector4": params.show_selection4
        }

    def _initmenu(self):
        screen = self.config.get_by_key("phonemenu")["init_screen"]
        self._change_screen(screen)
        self.gui.print_terminal("Menu initialized, starting screen: {}".format(screen))

    def _change_screen(self, screen):
        screenid = self.config.get_by_key("phonemenu")["screens"][screen]["screenid"]
        self.active_screen = screen
        self.output_queue.add((self.menu_osc_int_parameter_map.get("screen"), screenid))
        for selector in self.config.get_by_key("phonemenu")["screens"][screen]["selectors"]:
            self.output_queue.add((self.menu_osc_bool_parameter_map.get(selector), self.config.get_by_key("phonemenu")["screens"][screen]["selectors"][selector]))

    def _screen_refresh(self):
        pass

        
    def handle_menu_input(self, button):
        choices = self.config.get_by_key("phonemenu")["screens"][self.active_screen]["choices"]
        if button in choices:
            match choices:
                case "menu":
                    self._change_screen()
            
        else:
            return

    def init(self):
        self._initmenu()

    def setqueues(self, main_queue, output_queue):
        self.main_queue = main_queue
        self.output_queue = output_queue
