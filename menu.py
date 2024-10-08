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
        self.call_start_time: float = 0
        self.callerid: str = ""
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
            "numberRow2Slot4": params.show_numberRow2Slot4,
            "delimiterRow1": params.show_delimiterRow1,
            "delimiterRow2": params.show_delimiterRow2
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
        self.active_dialog = ""
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
        self._handle_numbers("row1", self.config.get_by_key("phonemenu")["screens"][screen]["numbers"]["row1"])
        self._handle_numbers("row2", self.config.get_by_key("phonemenu")["screens"][screen]["numbers"]["row2"])
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
        self._handle_numbers("row1", self.config.get_by_key("phonemenu")["dialogs"][dialog]["numbers"]["row1"])
        self._handle_numbers("row2", self.config.get_by_key("phonemenu")["dialogs"][dialog]["numbers"]["row2"])
        for selector in self.config.get_by_key("phonemenu")["screens"][self.active_screen]["selectors"]:
            self.osc.client.send_message(
                self.osc_bool_parameters.get(selector),
                False
                )

    def _redraw(self):
        self.gui.print_terminal("log_verbose: Redrawing screen") if self.config.get_by_key("log_verbose") else None
        self.osc.client.send_message(self.osc_integer_parameters.get("screen"), self.config.get_by_key("phonemenu")["screens"][self.active_screen]["screenid"])
        match self.active_mode:
            case 0:
                self.osc.client.send_message(self.osc_integer_parameters.get("window"), self.config.get_by_key("phonemenu")["screens"][self.active_screen]["window"])
                self._handle_numbers("row1", self.config.get_by_key("phonemenu")["screens"][self.active_screen]["numbers"]["row1"])
                self._handle_numbers("row2", self.config.get_by_key("phonemenu")["screens"][self.active_screen]["numbers"]["row2"])
                for selector in self.config.get_by_key("phonemenu")["screens"][self.active_screen]["selectors"]:
                    self.osc.client.send_message(
                        self.osc_bool_parameters.get(selector),
                        self.config.get_by_key("phonemenu")["screens"][self.active_screen]["selectors"][selector]
                        )
            case 1:
                self.osc.client.send_message(self.osc_integer_parameters.get("dialog"), self.config.get_by_key("phonemenu")["dialogs"][self.active_dialog]["dialog"])
                self.osc.client.send_message(self.osc_integer_parameters.get("popup"), self.config.get_by_key("phonemenu")["dialogs"][self.active_dialog]["popup"])
                self.osc.client.send_message(self.osc_integer_parameters.get("window"), self.config.get_by_key("phonemenu")["dialogs"][self.active_dialog]["window"])
                self._handle_numbers("row1", self.config.get_by_key("phonemenu")["dialogs"][self.active_dialog]["numbers"]["row1"])
                self._handle_numbers("row2", self.config.get_by_key("phonemenu")["dialogs"][self.active_dialog]["numbers"]["row2"])

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
            case "phonebook_switch":
                self._phonebook_switch_entry(choice[1])
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
        match self.active_mode:
            case 0:
                if button in self.config.get_by_key("phonemenu")["screens"][self.active_screen]["choices"]:
                    choice = self.config.get_by_key("phonemenu")["screens"][self.active_screen]["choices"][button]
                    self._handle_choices(choice)
                else:
                    return
            case 1:
                if button in self.config.get_by_key("phonemenu")["dialogs"][self.active_dialog]["choices"]:
                    choice = self.config.get_by_key("phonemenu")["dialogs"][self.active_dialog]["choices"][button]
                    self._handle_choices(choice)
                else:
                    return
            
    def _handle_callback_input(self, command, caller):        
        self.gui.print_terminal("log_verbose: Handle callback command: {}, caller: {} active_mode: {}".format(command, caller, self.active_mode)) if self.config.get_by_key("log_verbose") else None
        self.callerid = caller
        match command:
            case "call_end" | "call_busy":
                self.gui.print_terminal("Call with {} ended after {} seconds".format(caller,int(time.time() - self.call_start_time)))
                self._show_dialog("call_end")
                time.sleep(self.config.get_by_key("interaction_timeout"))
                self._reset_dialogs()
                self.call_start_time = float(0)
                self.callerid = ""
            case "call_outgoing":
                self.gui.print_terminal("Outgoing call to {}".format(caller))
                self._show_dialog("call_outgoing")
            case "call_incoming":
                self.gui.print_terminal("Incoming call from {}".format(caller))
                self._show_dialog("call_incoming")
            case "call_start":
                self.call_start_time = time.time()
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
                    return
            case "prev":
                if len_entries > 1:
                    if active_entry == 0:
                        self.active_phonebook_entry = len_entries - 1
                    else:
                        self.active_phonebook_entry -= 1
                else:
                    return
            case _:
                return
        self._redraw()
        self.gui.print_terminal("log_verbose: Switched phonebook in direction: {} new entry: {}".format(direction, self.active_phonebook_entry)) if self.config.get_by_key("log_verbose") else None

    def _handle_numbers(self, row, number_type):
        match number_type:
            case "phonebook":
                self._show_number_field(row, self.config.get_by_key("phonebook")[self.active_phonebook_entry][1])
            case "entry":
                self._show_number_field(row,  str(self.active_phonebook_entry + 1))
            case "callerid":
                self._show_number_field(row, self.callerid)
            case "calltimer":
                self._show_number_field(row, str(int(time.time() - self.call_start_time)))
            case "systemtime":
                self._show_number_field(row, "1337")
            case _:
                self._hide_number_field(row)
        self.gui.print_terminal("log_verbose: Handled number type: {} for row: {}".format(number_type, row)) if self.config.get_by_key("log_verbose") else None

    def _show_number_field(self, row, number):
        digitlist = list()
        for digit in "{s:{c}^{n}}".format(s = number, n = 4, c = "X"):
            match digit:
                case "*":
                    digitlist.append(11)
                case "#":
                    digitlist.append(12)
                case "X":
                    digitlist.append(255)
                case _:
                    digitlist.append(int(digit))
        match row:
            case "row1":
                self.osc.client.send_message(params.show_numberRow1Slot1, digitlist[0])
                self.osc.client.send_message(params.show_numberRow1Slot2, digitlist[1])
                self.osc.client.send_message(params.show_numberRow1Slot3, digitlist[2])
                self.osc.client.send_message(params.show_numberRow1Slot4, digitlist[3])
            case "row2":
                self.osc.client.send_message(params.show_numberRow2Slot1, digitlist[0])
                self.osc.client.send_message(params.show_numberRow2Slot2, digitlist[1])
                self.osc.client.send_message(params.show_numberRow2Slot3, digitlist[2])
                self.osc.client.send_message(params.show_numberRow2Slot4, digitlist[3])

    def _hide_number_field(self, row):
        match row:
            case "row1":
                self.osc.client.send_message(params.show_numberRow1Slot1, 255)
                self.osc.client.send_message(params.show_numberRow1Slot2, 255)
                self.osc.client.send_message(params.show_numberRow1Slot3, 255)
                self.osc.client.send_message(params.show_numberRow1Slot4, 255)
            case "row2":
                self.osc.client.send_message(params.show_numberRow2Slot1, 255)
                self.osc.client.send_message(params.show_numberRow2Slot2, 255)
                self.osc.client.send_message(params.show_numberRow2Slot3, 255)
                self.osc.client.send_message(params.show_numberRow2Slot4, 255)

    def _update_timers(self):
        match self.active_mode:
            case 0:
                row1 = self.config.get_by_key("phonemenu")["screens"][self.active_screen]["numbers"]["row1"]
                row2 = self.config.get_by_key("phonemenu")["screens"][self.active_screen]["numbers"]["row2"]
            case 1:
                row1 = self.config.get_by_key("phonemenu")["dialogs"][self.active_dialog]["numbers"]["row1"]
                row2 = self.config.get_by_key("phonemenu")["dialogs"][self.active_dialog]["numbers"]["row2"]
            case _:
                return
        if row1 == "calltimer" or row1 == "systemtime":
            self._handle_numbers("row1", row1)
        if row2 == "calltimer" or row2 == "systemtime":
            self._handle_numbers("row2", row2)

    def _worker_thread(self):
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
                if self.call_start_time is not float(0):
                    self._update_timers()
            except RuntimeError:
                pass
            time.sleep(.025)

    def run(self):
        self._initmenu()
        threading.Thread(target=self._worker_thread, daemon=True).start()
