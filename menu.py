from config import Config
from gui import Gui
from microsip import MicroSIP
import time
import params

class Menu:
    def  __init__(self, config: Config, gui: Gui, osc_client, microsip: MicroSIP):
        self.config = config
        self.gui = gui
        self.microsip = microsip
        self.osc_client = osc_client
        self.active_screen: str = ""
        self.active_dialog: str = ""
        self.active_mode = 0
        self.verbose = True
        self.osc_integer_parameters: dict[str, str] = {
            "screen": params.show_screen,
            "dialog": params.show_dialog,
            "popup": params.show_popup
        }
        self.osc_bool_parameters: dict[str, str] = {
            "selector1": params.show_selection1,
            "selector2": params.show_selection2,
            "selector3": params.show_selection3,
            "selector4": params.show_selection4
        }
        self.microsip_dialog_mapping: dict[str, tuple] = {
            "cmdCallEnd": ("call_ended", params.call_ended),
            "cmdIncomingCall": ("call_incoming", params.call_incoming),
            "cmdOutgoingCall": ("call_outgoing", params.call_outgoing),
            "cmdCallStart": ("call_started", params.call_started),
        }

    def _initmenu(self):
        screen = self.config.get_by_key("phonemenu")["init_screen"]
        self._switch_screen(screen)
        self._reset_dialogs()
        self.gui.print_terminal("Menu initialized, starting screen: {}".format(screen))

    def _reset_dialogs(self):
        self.active_mode = 0
        self.osc_client.send_message(self.osc_integer_parameters.get("dialog"), 0)
        self.osc_client.send_message(self.osc_integer_parameters.get("popup"), 0)
        for selector in self.config.get_by_key("phonemenu")["screens"][self.active_screen]["selectors"]:
            self.osc_client.send_message(
                self.osc_bool_parameters.get(selector),
                self.config.get_by_key("phonemenu")["screens"][self.active_screen]["selectors"][selector]
                )

    def _switch_screen(self, screen):
        self.active_screen = screen
        self.active_mode = 0
        self.osc_client.send_message(self.osc_integer_parameters.get("screen"), self.config.get_by_key("phonemenu")["screens"][screen]["screenid"])
        for selector in self.config.get_by_key("phonemenu")["screens"][screen]["selectors"]:
            self.osc_client.send_message(
                self.osc_bool_parameters.get(selector),
                self.config.get_by_key("phonemenu")["screens"][screen]["selectors"][selector]
                )
            
    def _show_dialog(self, dialog):
        self.active_dialog = dialog
        self.active_mode = 1
        self.osc_client.send_message(self.osc_integer_parameters.get("dialog"), self.config.get_by_key("phonemenu")["dialogs"][dialog]["dialog"])
        self.osc_client.send_message(self.osc_integer_parameters.get("popup"), self.config.get_by_key("phonemenu")["dialogs"][dialog]["popup"])
        for selector in self.config.get_by_key("phonemenu")["screens"][self.active_screen]["selectors"]:
            self.osc_client.send_message(
                self.osc_bool_parameters.get(selector),
                False
                )

    def _redraw(self):
        self.osc_client.send_message(self.osc_integer_parameters.get("screen"), self.config.get_by_key("phonemenu")["screens"][self.active_screen]["screenid"])
        for selector in self.config.get_by_key("phonemenu")["screens"][self.active_screen]["selectors"]:
            self.osc_client.send_message(
                self.osc_bool_parameters.get(selector),
                self.config.get_by_key("phonemenu")["screens"][self.active_screen]["selectors"][selector]
                )
        if self.active_mode == 1:
            self.osc_client.send_message(self.osc_integer_parameters.get("dialog"), self.config.get_by_key("phonemenu")["dialogs"][self.active_dialog]["dialog"])
            self.osc_client.send_message(self.osc_integer_parameters.get("popup"), self.config.get_by_key("phonemenu")["dialogs"][self.active_dialog]["popup"])

    def _handle_choices(self, choice):
        match choice[0]:
            case "screen":
                self._switch_screen(choice[1])
            case "call_accept":
                self.microsip.run_phone_command("answer")
            case "call_hangup":
                self.microsip.run_phone_command("hangup")
            case "call_phonebook":
                self.microsip.run_phone_command("phonebook", choice[1])
            case _:
                pass

    def handle_button_input(self, button):
        if self.active_mode == 0:
            if button[1] in self.config.get_by_key("phonemenu")["screens"][self.active_screen]["choices"]:
                choice = self.config.get_by_key("phonemenu")["screens"][self.active_screen]["choices"][button[1]]
                self._handle_choices(choice)
            else:
                return
        elif self.active_mode == 1:
            if button[1] in self.config.get_by_key("phonemenu")["dialogs"][self.active_dialog]["choices"]:
                choice = self.config.get_by_key("phonemenu")["dialogs"][self.active_dialog]["choices"][button[1]]
                self._handle_choices(choice)
            else:
                return
        elif self.active_mode == 2:
            #Loading transition mode, we don't accept input here
            return
            
    def handle_callback_input(self, command, caller):
        match command:
            case "cmdCallEnd" | "cmdCallBusy":
                self._show_dialog(self.microsip_dialog_mapping.get("cmdCallEnd")[0])
                time.sleep(2)
                self._reset_dialogs()
            case "cmdOutgoingCall":
                self._show_dialog(self.microsip_dialog_mapping.get("cmdOutgoingCall")[0])
            case "cmdIncomingCall":
                self._show_dialog(self.microsip_dialog_mapping.get("cmdIncomingCall")[0])
            case "cmdCallStart":
                self._show_dialog(self.microsip_dialog_mapping.get("cmdCallStart")[0])
            case _:
                return

    def init(self):
        self._initmenu()
