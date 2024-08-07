# pyright: reportMissingImports=false
from pythonosc import dispatcher
from config import Config
from gui import Gui
from microsip import MicroSIP
from menu import Menu
import params
import time
import threading

class VRPhone:
    def __init__(self, config: Config, gui: Gui, microsip: MicroSIP, osc_client, menu: Menu):
        self.config = config
        self.gui = gui
        self.micropsip = microsip
        self.osc_client = osc_client
        self.menu = menu
        self.input_queue: set = set()
        self.output_queue: set = set()
        self.main_queue: set = set()
        self.last_interaction = time.time() - self.config.get_by_key("interaction_timeout")
        self.is_paused = False
        self.osc_bool_parameter_commands: dict[str, tuple] = {
            params.receiver_button: ("receiver", None),
            params.pickup_button: ("answer", None),
            params.hangup_button: ("hangup", None),
            params.phonebook_entry_1_button: ("phonebook", 0),
            params.phonebook_entry_2_button: ("phonebook", 1),
            params.phonebook_entry_3_button: ("phonebook", 2),
            params.phonebook_entry_4_button: ("phonebook", 3)
        }
        #(parameter, (string("name"), float("menutimeout") ))
        self.osc_bool_parameter_buttons: dict[str, tuple] = {
            params.keypad_button: ("keypad_button", 1.0),
            params.center_button: ("center_button", 1.0),
            params.ok_button: ("ok_button", 1.0),
            params.cancel_button: ("cancel_button", 1.0),
            params.yes_button: ("yes_button", 1.0),
            params.no_button: ("no_button", 1.0)
        }

    def handle_event(self, eventdata):
        match eventdata[0]:
            case "osc":
                self.micropsip.update_osc_state(eventdata[1], eventdata[2])
            case "interaction":
                self.micropsip.run_phone_command(eventdata[1], eventdata[2])
            case _:
                print("Unknown event")
    
    def toggle_interactions(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.gui.print_terminal(
                "Interactions Paused.")
        else:
            self.gui.print_terminal(
                "Interactions Continued.")
    
    def _output_worker(self):
        while True:
            try:
                for address, value in self.output_queue:
                    self.osc_client.send_message(address, value)
                    self.output_queue.discard((address, value))
            except RuntimeError:
                pass
            time.sleep(.025)

    def _input_worker(self):
        while True:
            try:
                for address in self.input_queue:
                    if address in self.osc_bool_parameter_commands:
                        interaction_type = self.osc_bool_parameter_commands.get(address)[0]
                        interaction_args = self.osc_bool_parameter_commands.get(address)[1]
                        self.main_queue.add(("interaction", None, (address, interaction_type, interaction_args)))
                    elif address in self.osc_bool_parameter_buttons:
                        button_type = self.osc_bool_parameter_buttons.get(address)[0]
                        button_timeout = time.time() + self.osc_bool_parameter_buttons.get(address)[1]
                        self.main_queue.add(("menubutton", None, (address, button_type, button_timeout)))
                    self.input_queue.discard(address)
            except RuntimeError:
                pass
            time.sleep(.05)

    def _main_worker(self):
        while True:
            try:
                for maintask in self.main_queue:
                    match maintask[0]:
                        case "interaction":
                            self.micropsip.run_phone_command(maintask[2][1], maintask[2][2])
                        case "menubutton":
                            if maintask[1] <= time.time():
                                self.menu.handle_menubutton_event(maintask[2])
                            else:
                                continue
                        case "microsip":
                            self.micropsip.handle_microsip_feedback(maintask[2])
                        case "event":
                            if maintask[1] <= time.time():
                                self.handle_event(maintask[2])
                            else:
                                continue
                        case _:
                            self.gui.print_terminal("Unknown task type in main queue.")
                    self.main_queue.discard(maintask)
            except RuntimeError:
                pass
            time.sleep(.025)

    def _menu_worker(self):
        while True:
            try:
                pass
            except RuntimeError:
                pass
            time.sleep(.025)

    def osc_collision(self, address: str, *args):
        if not self.is_paused and (self.last_interaction + self.config.get_by_key("interaction_timeout")) <= time.time():
            if address in self.osc_bool_parameter_commands or address in self.osc_bool_parameter_buttons:
                self.last_interaction = time.time()
                if len(args) != 1:
                    return
                was_entered: bool = args[0]
                if type(was_entered) != bool:
                    return
                if was_entered and address not in self.input_queue:
                    self.input_queue.add(address)

    def map_parameters(self, dispatcher: dispatcher.Dispatcher):
        dispatcher.set_default_handler(self.osc_collision)
    
    def run(self):
        self.gui.on_toggle_interaction_clicked.add_listener(self.toggle_interactions)
        threading.Thread(target=self._output_worker, daemon=True).start()
        threading.Thread(target=self._input_worker, daemon=True).start()
        threading.Thread(target=self._main_worker, daemon=True).start()
