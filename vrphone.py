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
        self.interaction_queue: set = set()
        self.callback_queue: set = set()
        self.command_queue: set = set()
        self.call_started = False
        self.call_ended = False
        self.call_incoming = False
        self.call_outgoing = False
        self.call_answered = False
        self.call_ring = False
        self.call_busy = False
        self.call_active = False
        self.is_paused = False
        self.osc_bool_parameters: dict[str, tuple] = {
            params.receiver_button: ("receiver", None),
            params.phonebook_entry_1_button: ("phonebook", 0),
            params.phonebook_entry_2_button: ("phonebook", 1),
            params.phonebook_entry_3_button: ("phonebook", 2),
            params.phonebook_entry_4_button: ("phonebook", 3)
        }
        self.osc_bool_microsip_parameters: dict[str, tuple] = {
            params.call_started: ("cmdCallStart", "Call started"),
            params.call_ended: ("cmdCallEnd", "Call ended"),
            params.call_incoming: ("cmdIncomingCall", "Call incoming"),
            params.call_outgoing: ("cmdOutgoingCall", "Call outgoing"),
            params.call_answered: ("cmdCallAnswer", "Call answered"),
            params.call_ring: ("cmdCallRing", "Phone ringing (Ring ring ring... VR Phone)"),
            params.call_busy: ("cmdCallBusy", "Busy signal")
        }

    def handle_receiver_button(self):
        if self.call_active:
            self.gui.print_terminal(
                "Hanging up the phone"
            )
            self.call_hangup()
        elif not self.call_active and self.call_incoming:
            self.gui.print_terminal(
                "Phone picked up"
            )
            self.call_pickup()
        return
    
    def call_pickup(self):
        self.call_active = True
        command = self.execute_microsip_command("/answer")
        return command
    
    def call_hangup(self):
        self.call_active = False
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

    # def handle_parameter_update(self, parameter):
    #     element_name = self.parameter_to_button_element.get(parameter)
    #     element_id = self.elements[element_name]
    #     existing_element_label = self.button_labels[element_name]
    #     result = "[" + existing_element_label + "]"
    #     if element_id is not None:
    #         dpg.configure_item(
    #             element_id, label=result
    #         )
 
    def interaction_handler(self) -> None:
        while True:
            try:
                self.gui.handle_active_button_reset()
                #Build command queue from interactions
                if len(self.interaction_queue) > 0:
                    for interaction in self.interaction_queue:
                        interaction_type = self.osc_bool_parameters.get(interaction)[0]
                        interaction_args = self.osc_bool_parameters.get(interaction)[1]
                        if interaction_type == "receiver" or interaction_type == "button":
                            self.gui.handle_active_button_update(
                                parameter=interaction)
                        self.command_queue.add((interaction, interaction_type, interaction_args))
                        self.interaction_queue.discard(interaction)
            except RuntimeError:  # race condition for set changing during iteration
                pass
            time.sleep(.05)

    def command_executor(self) -> None:
        while True:
            try:
                #Run commands
                if len(self.command_queue) > 0:
                    for command in self.command_queue:
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
                        self.command_queue.discard(command)
            except RuntimeError:
                pass
            time.sleep(.05)

    def callback_handler(self) -> None:
        while True:
            try:
                #Handle callback
                if len(self.callback_queue) > 0:
                    for callback in self.callback_queue:
                        for parameter in self.osc_bool_microsip_parameters:
                            command = self.osc_bool_microsip_parameters.get(parameter)[0]
                            prettyname = self.osc_bool_microsip_parameters.get(parameter)[1]
                            if command == callback[0]:
                                self.gui.print_terminal("Microsip: {} ({}) Caller ID:{}".format(prettyname, command, callback[1]))
                        self.callback_queue.discard(callback)
            except RuntimeError:
                pass
            time.sleep(.05)

    def on_collission_enter(self, address: str, *args) -> None:
        if address in self.osc_bool_parameters and not self.is_paused:
            if len(args) != 1:
                return
            was_entered: bool = args[0]
            if type(was_entered) != bool:
                return
            if was_entered and address not in self.interaction_queue:
                self.interaction_queue.add(address)
        time.sleep(self.config.get_by_key("interaction_timeout"))

    def microsip_callback(self, microsip_cmd: str, caller_id: str) -> None:
        try:
            self.callback_queue.add((microsip_cmd, caller_id))
        except:
            pass

    def map_parameters(self, dispatcher: dispatcher.Dispatcher) -> None:
        dispatcher.set_default_handler(self.on_collission_enter)

    def init(self) -> None:
        self.gui.on_toggle_interaction_clicked.add_listener(
            self.toggle_interactions)
