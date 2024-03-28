# pyright: reportMissingImports=false
from pythonosc import dispatcher
from config import Config
from gui import Gui
import params
import time
import subprocess

class VRPhone:
    def __init__(self, config: Config, gui: Gui, osc_client):
        self.config = config
        self.gui = gui
        self.osc_client = osc_client
        self.active_interactions: set = set()
        self.call_started = False
        self.call_ended = False
        self.call_incoming = False
        self.call_outgoing = False
        self.call_answered = False
        self.call_ring = False
        self.call_busy = False
        self.call_active = False
        self.is_paused = False
        self.last_command_run = time.time()
        self.osc_bool_parameters: dict[str, tuple] = {
            params.receiver_button: ("receiver", None),
            params.phonebook_entry_1_button: ("phonebook", 0),
            params.phonebook_entry_2_button: ("phonebook", 1),
            params.phonebook_entry_3_button: ("phonebook", 2),
            params.phonebook_entry_4_button: ("phonebook", 3)
        }
        self.osc_bool_microsip_parameters: dict[str, str] = {
            params.call_started: "cmdCallStart",
            params.call_ended: "cmdCallEnd",
            params.call_incoming: "cmdIncomingCall",
            params.call_outgoing: "cmdOutgoingCall",
            params.call_answered: "cmdCallAnswer",
            params.call_ring: "cmdCallRing",
            params.call_busy: "cmdCallBusy"
        }

    def handle_receiver_button(self):
        if self.call_active:
            self.call_hangup()
        elif not self.call_active and self.call_incoming:
            self.call_pickup()
        return
    
    def call_pickup(self):
        self.gui.print_terminal(
            "Call pickup"
        )
        command = self.execute_microsip_command("/answer")
        return command
    
    def call_hangup(self):
        self.gui.print_terminal(
            "Call hangup"
        )
        command = self.execute_microsip_command("/hangupall")
        return command

    def handle_phonebook_entry(self, entry):
        if not self.call_active:
            for p, (name, number) in enumerate(self.config.get_by_key("phonebook")):
                if p == entry:
                    self.gui.print_terminal(
                            "Call phone book entry #{} {} {}".format(p+1, name, number)
                    )
                    self.call_active = True
                    return self.execute_microsip_command(number)
        else:
            self.gui.print_terminal(
                    "Call already active, ignoring phone book button action"
            )

    def toggle_interactions(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.gui.print_terminal(
                "Interactions Paused.")
        else:
            self.gui.print_terminal(
                "Interactions Continued.")

    def execute_microsip_command(self, parameter: str):
        microsip_binary = self.config.get_by_key("microsip_binary")
        command = subprocess.run([microsip_binary, parameter])
        return command

    def watch(self) -> None:
        while True:
            try:
                self.gui.handle_active_button_reset()

                if len(self.active_interactions) > 0 and not self.is_paused:
                    commands = []
                    current_time = time.time()
                    for interaction in self.active_interactions:
                        if current_time + self.config.get_by_key("interaction_timeout") < self.last_command_run: break
                        interaction_type = self.osc_bool_parameters.get(interaction)[0]
                        interaction_args = self.osc_bool_parameters.get(interaction)[1]
                        if interaction_type == "receiver" or interaction_type == "button":
                            self.gui.handle_active_button_update(
                                parameter=interaction)
                        self.last_command_run = time.time()
                        commands.append((interaction, interaction_type, interaction_args))
                    if len(commands) > 0:
                        for command in commands:
                            interaction = command[0]
                            interaction_type = command[1]
                            interaction_args = command[2]
                            match interaction_type:
                                case "receiver":
                                    #Add more logic!
                                    self.handle_receiver_button()                               
                                case "phonebook":
                                    self.handle_phonebook_entry(interaction_args)
                                case _:
                                    self.gui.print_terminal("Unknown type?")
                            time.sleep(self.config.get_by_key("interaction_timeout"))
            except RuntimeError:  # race condition for set changing during iteration
                pass
            time.sleep(.05)

    def on_collission_enter(self, address: str, *args) -> None:
        if address in self.osc_bool_parameters:
            if len(args) != 1:
                return
            was_entered: bool = args[0]
            if type(was_entered) != bool:
                return
            if was_entered:
                self.active_interactions.add(address)
            else:
                self.active_interactions.discard(address)

    def microsip_callback(self, microsip_cmd: str, caller_id: str) -> None:
        match microsip_cmd:
            case "cmdCallStart":
                self.call_started = True
                self.call_ended = False
                self.gui.print_terminal("Call started")
            case "cmdCallEnd":
                self.call_ended = True
                self.call_started = False
                self.call_incoming = False
                self.call_active = False
                self.gui.print_terminal("Call ended")
            case "cmdIncomingCall":
                self.call_incoming = True
                self.call_outgoing = False
                self.call_ended = False
                self.gui.print_terminal("Call incoming")
            case "cmdOutgoingCall":
                self.call_outgoing = True
                self.call_incoming = False
                self.call_ended = False
            case "cmdCallAnswer":
                self.call_answered = True
                self.call_active = True
                self.call_ended = False
                self.gui.print_terminal("Call answered")
            case _:
                print("Unknown microsip callback command received: {}".format(microsip_cmd))

    def map_parameters(self, dispatcher: dispatcher.Dispatcher) -> None:
        dispatcher.set_default_handler(self.on_collission_enter)

    def init(self) -> None:
        self.gui.on_toggle_interaction_clicked.add_listener(
            self.toggle_interactions)
