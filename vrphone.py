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
        self.input_queue: set = set()
        self.output_queue: set = set()
        self.main_queue: set = set()
        self.last_interaction = time.time() - self.config.get_by_key("interaction_timeout")
        self.call_active = False
        self.call_outgoing = False
        self.call_incoming = False
        self.is_paused = False
        self.osc_bool_parameters: dict[str, tuple] = {
            params.receiver_button: ("receiver", None),
            params.pickup_button: ("pickup", None),
            params.hangup_button: ("hangup", None),
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
        if (self.call_active and not self.call_incoming and not self.call_outgoing):
            self.gui.print_terminal(
                "Hanging up the phone"
            )
            self.call_hangup()
        elif (not self.call_active and self.call_incoming and not self.call_outgoing):
            self.gui.print_terminal(
                "Phone picked up"
            )
            self.call_pickup()
        return
    
    def call_pickup(self):
        self.call_active = True
        self.call_outgoing = False
        self.call_incoming = False
        command = self.execute_microsip_command("/answer")
        return command
    
    def call_hangup(self):
        self.call_active = False
        self.call_outgoing = False
        self.call_incoming = False
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

    def execute_microsip_command(self, parameter: str):
        microsip_binary = self.config.get_by_key("microsip_binary")
        command = subprocess.run([microsip_binary, parameter])
        return command
    
    def toggle_interactions(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.gui.print_terminal(
                "Interactions Paused.")
        else:
            self.gui.print_terminal(
                "Interactions Continued.")
    
    def output_handler(self) -> None:
        while True:
            try:
                for output in self.output_queue:
                    for parameter in self.osc_bool_microsip_parameters:
                        if parameter == output:
                            self.osc_client.send_message(parameter, True)
                    self.output_queue.discard(output)
            except RuntimeError: # race condition for set changing during iteration
                pass
            time.sleep(.05)

    def input_handler(self) -> None:
        while True:
            try:
                self.gui.handle_active_button_reset()
                for address in self.input_queue:
                    interaction_type = self.osc_bool_parameters.get(address)[0]
                    interaction_args = self.osc_bool_parameters.get(address)[1]
                    self.main_queue.add(("interaction", address, (interaction_type, interaction_args)))
                    self.input_queue.discard(address)
            except RuntimeError:  # race condition for set changing during iteration
                pass
            time.sleep(.05)

    def main_handler(self) -> None:
        while True:
            try:
                #Run tasks
                for task in self.main_queue:
                    #tuple format:
                    #str(type) str(address) tuple(taskdata)
                    type = task[0]
                    address = task[1]
                    taskdata = task[2]
                    match type:
                        case "interaction":
                            match taskdata[0]:
                                case "receiver":
                                    self.handle_receiver_button()
                                case "pickup":
                                    self.call_pickup()
                                case "hangup":
                                    self.call_hangup()
                                case "phonebook":
                                    self.handle_phonebook_entry(taskdata[1])
                        case "microsip":
                            if (taskdata[0] == "cmdCallEnd") or (taskdata[0] == "cmdCallBusy"):
                                self.call_active = False
                                self.call_outgoing = False
                                self.call_incoming = False
                                self.gui.print_terminal("{}: {}".format(taskdata[1], taskdata[2]))
                            elif taskdata[0] == "cmdOutgoingCall":
                                self.call_active = False
                                self.call_outgoing = True
                                self.call_incoming = False
                                self.gui.print_terminal("{}: {}".format(taskdata[1], taskdata[2]))
                            elif taskdata[0] == "cmdIncomingCall":
                                self.call_active = False
                                self.call_outgoing = False
                                self.call_incoming = True
                                self.gui.print_terminal("{}: {}".format(taskdata[1], taskdata[2]))
                            elif taskdata[0] == "cmdCallStart":
                                self.call_active = True
                                self.call_outgoing = False
                                self.call_incoming = False
                                self.gui.print_terminal("{}: {}".format(taskdata[1], taskdata[2]))
                            self.output_queue.add(address)
                    self.main_queue.discard(task)
            except RuntimeError:
                pass
            time.sleep(.05)

    def microsip_handler(self, microsip_cmd: str, caller_id: str) -> None:
        for parameter in self.osc_bool_microsip_parameters:
            command = self.osc_bool_microsip_parameters.get(parameter)[0]
            prettyname = self.osc_bool_microsip_parameters.get(parameter)[1]
            if command == microsip_cmd:
                self.main_queue.add(("microsip", parameter, (microsip_cmd, prettyname, caller_id)))

    def osc_collision(self, address: str, *args) -> None:
        if address in self.osc_bool_parameters and not self.is_paused and (self.last_interaction + self.config.get_by_key("interaction_timeout")) <= time.time():
            self.last_interaction = time.time()
            if len(args) != 1:
                return
            was_entered: bool = args[0]
            if type(was_entered) != bool:
                return
            if was_entered and address not in self.input_queue:
                self.input_queue.add(address)

    def map_parameters(self, dispatcher: dispatcher.Dispatcher) -> None:
        dispatcher.set_default_handler(self.osc_collision)

    def init(self) -> None:
        self.gui.on_toggle_interaction_clicked.add_listener(
            self.toggle_interactions)
