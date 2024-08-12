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
    def __init__(self, config: Config, gui: Gui, osc_client):
        self.config = config
        self.gui = gui
        self.osc_client = osc_client
        self.microsip = MicroSIP(config=self.config, gui=self.gui)
        self.menu = Menu(config=self.config, gui=self.gui, osc_client=self.osc_client, microsip=self.microsip)
        self.input_queue: set = set()
        self.last_interactions: dict = dict()
        self.is_paused = False
        self.verbose = False
        self.avatar_change_input = params.avatar_change
        self.osc_bool_inputs: dict[str, tuple] = {
            params.receiver_button: ("interaction", "answer", None),
            params.pickup_button: ("interaction", "answer", None),
            params.hangup_button: ("interaction", "hangup", None),
            params.phonebook_entry_1_button: ("interaction", "phonebook", 0),
            params.phonebook_entry_2_button: ("interaction", "phonebook", 1),
            params.phonebook_entry_3_button: ("interaction", "phonebook", 2),
            params.phonebook_entry_4_button: ("interaction", "phonebook", 3),
            params.keypad_button: ("menubutton", "keypad_button", 1.0),
            params.center_button: ("menubutton", "center_button", 1.0),
            params.ok_button: ("menubutton", "ok_button", 1.0),
            params.cancel_button: ("menubutton", "cancel_button", 1.0),
            params.yes_button: ("menubutton", "yes_button", 1.0),
            params.no_button: ("menubutton", "no_button", 1.0)
        }

    def toggle_interactions(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.gui.print_terminal(
                "Interactions Paused.")
        else:
            self.gui.print_terminal(
                "Interactions Continued.")

    def _input_worker(self):
        while True:
            try:
                for address in self.input_queue:
                    match self.osc_bool_inputs.get(address)[0]:
                        case "interaction":
                            interaction_type = self.osc_bool_inputs.get(address)[1]
                            interaction_args = self.osc_bool_inputs.get(address)[2]
                            self.microsip.run_phone_command(interaction_type, interaction_args)
                        case "menubutton":
                            button_type = self.osc_bool_inputs.get(address)[1]
                            button_timeout = time.time() + self.osc_bool_inputs.get(address)[2]
                            self.menu.handle_button_input((address, button_type, button_timeout))
                    self.input_queue.discard(address)
            except RuntimeError:
                pass
            time.sleep(.05)

    def osc_collision(self, address: str, *args):
        if address == self.avatar_change_input:
            self.avatar_change()
            return
        if not self.is_paused:
            if address in self.osc_bool_inputs:
                if address in self.last_interactions and (self.last_interactions[address] + self.config.get_by_key("interaction_timeout")) > time.time():
                    return
                if len(args) != 1:
                    return
                was_entered: bool = args[0]
                if type(was_entered) != bool:
                    return
                if was_entered and address not in self.input_queue:
                    self.input_queue.add(address)
                    self.last_interactions[address] = time.time()

    def microsip_callback(self, microsip_cmd: str, caller_id: str):
        self.menu.handle_callback_input(microsip_cmd, caller_id)

    def map_parameters(self, dispatcher: dispatcher.Dispatcher):
        dispatcher.set_default_handler(self.osc_collision)

    def avatar_change(self):
        self.gui.print_terminal("Avatar change, redrawing menu")
        self.menu._redraw()

    def run(self):
        self.menu.init()
        self.gui.on_toggle_interaction_clicked.add_listener(self.toggle_interactions)
        threading.Thread(target=self._input_worker, daemon=True).start()
