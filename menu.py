from config import Config
from gui import Gui
from microsip import MicroSIP
from osc import Osc
import time
import params
import threading

class Menu:
    def  __init__(self, config: Config, gui: Gui, osc: Osc, microsip: MicroSIP, osc_vrc_queue: set = set(), osc_microsip_queue: set = set()):
        self.config = config
        self.gui = gui
        self.microsip = microsip
        self.osc = osc
        self.osc_vrc_queue = osc_vrc_queue
        self.osc_microsip_queue = osc_microsip_queue
        self.active_screen: str = ""
        self.active_dialog: str = ""
        self.active_mode: int = 0
        self.active_phonebook_entry: int = 0
        self.call_start_time: float = float()
        self.osc_integer_parameters: dict[str, str] = {
            "screen": params.active_screen,
            "window": params.active_window,
            "dialog": params.active_dialog,
            "popup": params.active_popup,
            "numberRow1Slot1": params.show_numberRow1Slot1,
            "numberRow1Slot2": params.show_numberRow1Slot2,
            "numberRow1Slot3": params.show_numberRow1Slot3,
            "numberRow1Slot4": params.show_numberRow1Slot4,
            "numberRow2Slot1": params.show_numberRow2Slot1,
            "numberRow2Slot2": params.show_numberRow2Slot2,
            "numberRow2Slot3": params.show_numberRow2Slot3,
            "numberRow2Slot4": params.show_numberRow2Slot4
        }
        self.osc_bool_parameters: dict[str, str] = {
            "selector1": params.show_selection1,
            "selector2": params.show_selection2,
            "selector3": params.show_selection3,
            "selector4": params.show_selection4
        }
        self.microsip_dialog_mapping: dict[str, str] = {
            params.microsip_call_outgoing: "call_outgoing",
            params.microsip_call_incoming: "call_incoming",
            params.microsip_call_ring: "call_ring",
            params.microsip_call_answer: "call_answer",
            params.microsip_call_busy: "call_busy",
            params.microsip_call_start: "call_start",
            params.microsip_call_end: "call_end",
        }
        self.vrc_button_mapping: dict[str, str] = {
            params.keypad_button: "keypad_button",
            params.center_button: "center_button",
            params.ok_button: "ok_button",
            params.cancel_button: "cancel_button",
            params.yes_button: "yes_button",
            params.no_button: "no_button"
        }

    def _initmenu(self):
        screen = self.config.get_by_key("phonemenu")["init_screen"]
        self._switch_screen(screen)
        self._reset_dialogs()
        self.gui.print_terminal("Menu: Avatar screen menu initialized")

    def _reset_dialogs(self):
        self.active_mode = 0
        self.osc.client.send_message(self.osc_integer_parameters.get("dialog"), 0)
        self.osc.client.send_message(self.osc_integer_parameters.get("popup"), 0)
        self.osc.client.send_message(self.osc_integer_parameters.get("window"), self.config.get_by_key("phonemenu")["screens"][self.active_screen]["window"])
        for selector in self.config.get_by_key("phonemenu")["screens"][self.active_screen]["selectors"]:
            self.osc.client.send_message(
                self.osc_bool_parameters.get(selector),
                self.config.get_by_key("phonemenu")["screens"][self.active_screen]["selectors"][selector]
                )

    def _switch_screen(self, screen):
        self.gui.print_terminal("log_verbose: Switching screen to: {}".format(screen)) if self.config.get_by_key("log_verbose") else None
        self.active_mode = 2
        self.osc.client.send_message(self.osc_integer_parameters.get("popup"), self.config.get_by_key("phonemenu")["transition_popup"])
        time.sleep(self.config.get_by_key("interaction_timeout"))
        self.osc.client.send_message(self.osc_integer_parameters.get("popup"), 0)
        self.active_screen = screen
        self.active_mode = 0
        self.osc.client.send_message(self.osc_integer_parameters.get("screen"), self.config.get_by_key("phonemenu")["screens"][screen]["screenid"])
        self.osc.client.send_message(self.osc_integer_parameters.get("window"), self.config.get_by_key("phonemenu")["screens"][screen]["window"])
        for selector in self.config.get_by_key("phonemenu")["screens"][screen]["selectors"]:
            self.osc.client.send_message(
                self.osc_bool_parameters.get(selector),
                self.config.get_by_key("phonemenu")["screens"][screen]["selectors"][selector]
                )
            
    def _show_dialog(self, dialog):
        self.gui.print_terminal("log_verbose: Showing dialog: {}".format(dialog)) if self.config.get_by_key("log_verbose") else None
        self.active_dialog = dialog
        self.active_mode = 1
        self.osc.client.send_message(self.osc_integer_parameters.get("dialog"), self.config.get_by_key("phonemenu")["dialogs"][dialog]["dialog"])
        self.osc.client.send_message(self.osc_integer_parameters.get("popup"), self.config.get_by_key("phonemenu")["dialogs"][dialog]["popup"])
        self.osc.client.send_message(self.osc_integer_parameters.get("window"), self.config.get_by_key("phonemenu")["dialogs"][dialog]["window"])
        for selector in self.config.get_by_key("phonemenu")["screens"][self.active_screen]["selectors"]:
            self.osc.client.send_message(
                self.osc_bool_parameters.get(selector),
                False
                )

    def _redraw(self):
        self.gui.print_terminal("log_verbose: Redrawing screen") if self.config.get_by_key("log_verbose") else None
        self.osc.client.send_message(self.osc_integer_parameters.get("screen"), self.config.get_by_key("phonemenu")["screens"][self.active_screen]["screenid"])
        self.osc.client.send_message(self.osc_integer_parameters.get("window"), self.config.get_by_key("phonemenu")["screens"][self.active_screen]["window"]) if self.active_mode == 0 else None
        for selector in self.config.get_by_key("phonemenu")["screens"][self.active_screen]["selectors"]:
            self.osc.client.send_message(
                self.osc_bool_parameters.get(selector),
                self.config.get_by_key("phonemenu")["screens"][self.active_screen]["selectors"][selector]
                )
        if self.active_mode == 1:
            self.osc.client.send_message(self.osc_integer_parameters.get("dialog"), self.config.get_by_key("phonemenu")["dialogs"][self.active_dialog]["dialog"])
            self.osc.client.send_message(self.osc_integer_parameters.get("popup"), self.config.get_by_key("phonemenu")["dialogs"][self.active_dialog]["popup"])
            self.osc.client.send_message(self.osc_integer_parameters.get("window"), self.config.get_by_key("phonemenu")["dialogs"][self.active_dialog]["window"])
        if self.active_mode == 2:
            self.osc.client.send_message(self.osc_integer_parameters.get("dialog"), self.config.get_by_key("phonemenu")["dialogs"][self.active_dialog]["dialog"])
            self.osc.client.send_message(self.osc_integer_parameters.get("popup"), self.config.get_by_key("phonemenu")["transition_popup"])
            self.osc.client.send_message(self.osc_integer_parameters.get("window"), self.config.get_by_key("phonemenu")["dialogs"][self.active_dialog]["window"])

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
            case "phonebook_next":
                self._phonebook_switch_entry("next")
            case "phonebook_prev":
                self._phonebook_switch_entry("prev")
            case "phonebook_call_confirm_dialog":
                self._phonebook_call_confirm_dialog()
            case "phonebook_call_active_entry":
                self.microsip.run_phone_command("phonebook", self.active_phonebook_entry)
            case "exit_dialogs":
                self._reset_dialogs()
            case _:
                pass

    def _handle_avatar_change(self):
        self.gui.print_terminal("Menu: Avatar change detected, redrawing screen")
        self._redraw()

    def _handle_button_input(self, button):
        self.gui.print_terminal("log_verbose: Handle button input: {} active_mode: {}".format(button, self.active_mode)) if self.config.get_by_key("log_verbose") else None
        if self.active_mode == 0:
            if button in self.config.get_by_key("phonemenu")["screens"][self.active_screen]["choices"]:
                choice = self.config.get_by_key("phonemenu")["screens"][self.active_screen]["choices"][button]
                self._handle_choices(choice)
            else:
                return
        elif self.active_mode == 1:
            if button in self.config.get_by_key("phonemenu")["dialogs"][self.active_dialog]["choices"]:
                choice = self.config.get_by_key("phonemenu")["dialogs"][self.active_dialog]["choices"][button]
                self._handle_choices(choice)
            else:
                return
        elif self.active_mode == 2:
            #Loading transition mode, we don't accept input here
            return
            
    def _handle_callback_input(self, command, caller):        
        self.gui.print_terminal("log_verbose: Handle callback command: {}, caller: {} active_mode: {}".format(command, caller, self.active_mode)) if self.config.get_by_key("log_verbose") else None
        match command:
            case "call_end" | "call_busy":
                self.gui.print_terminal("Call with {} ended after {} seconds".format(caller,int(time.time() - self.call_start_time)))
                self._show_dialog("call_end")
                time.sleep(self.config.get_by_key("interaction_timeout"))
                self._reset_dialogs()
            case "call_outgoing":
                self.call_start_time = time.time()
                self.gui.print_terminal("Outgoing call to {}".format(caller))
                self._show_dialog("call_outgoing")
            case "call_incoming":
                self.call_start_time = time.time()
                self.gui.print_terminal("Incoming call from {}".format(caller))
                self._show_dialog("call_incoming")
            case "call_start":
                self.gui.print_terminal("Call with {} started".format(caller))
                self._show_dialog("call_start")
            case _:
                self.gui.print_terminal("log_verbose: Unhandled callback command: {}".format(command)) if self.config.get_by_key("log_verbose") else None
                return

    def _phonebook_switch_entry(self, direction):
        active_entry = self.active_phonebook_entry
        len_entries = len(self.config.get_by_key("phonebook"))
        match direction:
            case "next":
                if len_entries > 1:
                    if active_entry == len_entries - 1:
                        self.active_phonebook_entry = 0
                    else:
                        self.active_phonebook_entry += 1
                else:
                    pass
            case "prev":
                if len_entries > 1:
                    if active_entry == 0:
                        self.active_phonebook_entry = len_entries - 1
                    else:
                        self.active_phonebook_entry -= 1
                else:
                    pass

    def _phonebook_call_confirm_dialog(self):
        self._show_dialog("call_confirm")
        #phonebook_call_confirm_menu
        pass

    def _input_worker(self):
        while True:
            try:
                #Handle VRC queue
                for address in self.osc_vrc_queue:
                    if address == self.osc.avatar_change_input:
                        self._handle_avatar_change()
                    else:
                        self._handle_button_input(self.vrc_button_mapping.get(address))        
                    self.osc_vrc_queue.discard(address)
                #Handle Microsip queue
                for address, caller in self.osc_microsip_queue:
                    self._handle_callback_input(self.microsip_dialog_mapping.get(address), caller)
                    self.osc_microsip_queue.discard((address, caller))
                #Handle call timer
                #self._handle_calltimer()
            except RuntimeError:
                pass
            time.sleep(.025)

    def run(self):
        self._initmenu()
        threading.Thread(target=self._input_worker, daemon=True).start()
