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
        self.active_screen: str = ""
        self.active_dialog: str = ""
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
        self._switch_screen(screen)
        self.gui.print_terminal("Menu initialized, starting screen: {}".format(screen))

    def _switch_screen(self, screen):
        screenid = self.config.get_by_key("phonemenu")["screens"][screen]["screenid"]
        self.active_screen = screenid
        self.output_queue.add((self.menu_osc_int_parameter_map.get("screen"), screenid))
        for selector in self.config.get_by_key("phonemenu")["screens"][screen]["selectors"]:
            self.output_queue.add((
                self.menu_osc_bool_parameter_map.get(selector),
                self.config.get_by_key("phonemenu")["screens"][screen]["selectors"][selector]
                ))
            
    def _show_dialog(self, dialog):
        self.active_dialog = dialog
        dialogid = self.config.get_by_key("phonemenu")["dialogs"][dialog]["dialog"]
        popupid = self.config.get_by_key("phonemenu")["dialogs"][dialog]["popup"]
        self.output_queue.add((self.menu_osc_int_parameter_map.get("dialog"), dialogid))
        self.output_queue.add((self.menu_osc_int_parameter_map.get("popup"), popupid))

    def _redraw(self):
        screen = self.active_screen
        screenid = self.config.get_by_key("phonemenu")["screens"][screen]["screenid"]
        dialog = self.active_dialog
        dialogid = self.config.get_by_key("phonemenu")["dialogs"][dialog]["dialog"]
        popupid = self.config.get_by_key("phonemenu")["dialogs"][dialog]["popup"]
        self.output_queue.add((self.menu_osc_int_parameter_map.get("screen"), screenid))
        self.output_queue.add((self.menu_osc_int_parameter_map.get("dialog"), dialogid))
        self.output_queue.add((self.menu_osc_int_parameter_map.get("popup"), popupid))
        for selector in self.config.get_by_key("phonemenu")["screens"][screen]["selectors"]:
            self.output_queue.add((
                self.menu_osc_bool_parameter_map.get(selector),
                self.config.get_by_key("phonemenu")["screens"][screen]["selectors"][selector]
                ))
            
    def _handle_dialog_choices(self, choice):
        match choice[0]:
            case "screen":
                self._switch_screen(choice[1])
            case "call_accept":
                #todo
                pass
            case "call_hangup":
                #todo
                pass
            case "call_phonebook":
                #todo
                pass
            case _:
                pass

    def handle_button_input(self, button):
        if self.active_dialog == "":
            choices = self.config.get_by_key("phonemenu")["screens"][self.active_screen]["choices"]
            if button in choices:
                choice = self.config.get_by_key("phonemenu")["screens"][self.active_screen]["choices"][button]
                self._handle_dialog_choices(choice)
            else:
                return
        elif self.active_dialog != "":
            choices = self.config.get_by_key("phonemenu")["screens"][self.active_screen]["choices"]
            if button in choices:
                choice = self.config.get_by_key("phonemenu")["screens"][self.active_screen]["choices"][button]
                self._handle_dialog_choices(choice)
            else:
                return


            
        

    def init(self):
        self._initmenu()

    def setqueues(self, main_queue, output_queue):
        self.main_queue = main_queue
        self.output_queue = output_queue
