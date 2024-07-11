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
        self.osc_bool_parameter_commands: dict[str, tuple] = {
            params.receiver_button: ("receiver", None),
            params.pickup_button: ("answer", None),
            params.hangup_button: ("hangup", None),
            params.phonebook_entry_1_button: ("phonebook", 0),
            params.phonebook_entry_2_button: ("phonebook", 1),
            params.phonebook_entry_3_button: ("phonebook", 2),
            params.phonebook_entry_4_button: ("phonebook", 3)
        }
        self.microsip_state_parameters: dict[str, tuple] = {
            "cmdCallStart": ("Call started", params.call_started),
            "cmdCallEnd": ("Call ended", params.call_ended),
            "cmdIncomingCall": ("Call incoming", params.call_incoming),
            "cmdOutgoingCall": ("Call outgoing", params.call_outgoing),
            "cmdCallAnswer": ("Call answered", params.call_answered),
            "cmdCallRing": ("Phone ringing (Ring ring ring... VR Phone)", params.call_ring),
            "cmdCallBusy": ("Busy signal", params.call_busy),
        }

    def receiver_button(self):
        if (self.call_active and not self.call_incoming and not self.call_outgoing):
            self.gui.print_terminal(
                "Hanging up the phone"
            )
            self.call_hangup()
        elif (not self.call_active and self.call_incoming and not self.call_outgoing):
            self.gui.print_terminal(
                "Phone picked up"
            )
            self.call_answer()
        return
    
    def call_answer(self):
        self.call_active = True
        self.call_outgoing = False
        self.call_incoming = False
        result = self.execute_microsip_command("/answer")
        return result
    
    def call_hangup(self, command = "hangupall"):
        self.call_active = False
        self.call_outgoing = False
        self.call_incoming = False
        result = self.execute_microsip_command("/" + command)
        return result

    def send_dtmf(self, code):
        result = self.execute_microsip_command("/dtmf:" + code)
        return result
    
    def call_transfer(self, number):
        result = self.execute_microsip_command("/transfer:" + number)
        return result

    def call_phonebook_entry(self, entry):
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

    def run_phone_command(self, command, args = None):
        match command:
            case "receiver":
                self.receiver_button()
            case "answer":
                self.call_answer()
            case "hangup":
                self.call_hangup()
            case "hangupcalling":
                self.call_hangup(command)
            case "hangupincoming":
                self.call_hangup(command)
            case "phonebook":
                self.call_phonebook_entry(args)
            case "dtmf":
                self.send_dtmf(args)
            case "transfer":
                self.call_transfer(args)

    def update_osc_state(self, tasktype, parameter = None):
        match tasktype:
            case "set":
                self.output_queue.add((parameter, True))
            case "reset":
                self.output_queue.add((parameter, False))
            case "resetall":
                for cmd in self.microsip_state_parameters:
                    self.output_queue.add((self.microsip_state_parameters.get(cmd)[1], False))
            case _:
                self.gui.print_terminal("Unknown OSC event: {}".format(tasktype))

    def handle_microsip_feedback(self, taskdata):
        if (taskdata[0] == "cmdCallEnd"):
            self.call_active = False
            self.call_outgoing = False
            self.call_incoming = False
            for cmd in ["cmdOutgoingCall", "cmdIncomingCall", "cmdCallStart", "cmdCallAnswer", "cmdCallRing"]:
                self.update_osc_state("reset", self.microsip_state_parameters.get(cmd)[1])
            self.main_queue.add(("event", time.time() + 1, ("osc", "reset", self.microsip_state_parameters.get("cmdCallEnd")[1])))
        elif taskdata[0] == "cmdOutgoingCall":
            self.call_active = False
            self.call_outgoing = True
            self.call_incoming = False
            for cmd in ["cmdCallEnd", "cmdCallBusy", "cmdIncomingCall", "cmdCallStart", "cmdCallAnswer", "cmdCallRing"]:
                self.update_osc_state("reset", self.microsip_state_parameters.get(cmd)[1])
        elif taskdata[0] == "cmdIncomingCall":
            self.call_active = False
            self.call_outgoing = False
            self.call_incoming = True
            for cmd in ["cmdCallEnd", "cmdCallBusy", "cmdOutgoingCall", "cmdCallStart", "cmdCallAnswer"]:
                self.update_osc_state("reset", self.microsip_state_parameters.get(cmd)[1])
        elif (taskdata[0] == "cmdCallStart") or (taskdata[0]  == "cmdCallAnswer"):
            self.call_active = True
            self.call_outgoing = False
            self.call_incoming = False
            for cmd in ["cmdCallEnd", "cmdCallBusy", "cmdCallRing"]:
                self.update_osc_state("reset", self.microsip_state_parameters.get(cmd)[1])
        self.gui.print_terminal("{}: {}".format(taskdata[1], taskdata[2]))
        self.update_osc_state("set", taskdata[3])
        if self.config.get_by_key("call_autoanswer") and taskdata[0] == "cmdIncomingCall":
            self.call_answer()


    def handle_event(self, eventdata) -> None:
        match eventdata[0]:
            case "osc":
                self.update_osc_state(eventdata[1], eventdata[2])
            case "interaction":
                self.run_phone_command(eventdata[1], eventdata[2])
            case _:
                print("Unknown event")

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
    
    def output_worker(self) -> None:
        while True:
            try:
                for address, value in self.output_queue:
                    self.osc_client.send_message(address, value)
                    self.output_queue.discard((address, value))
            except RuntimeError:
                pass
            time.sleep(.05)

    def input_worker(self) -> None:
        while True:
            try:
                for address in self.input_queue:
                    interaction_type = self.osc_bool_parameter_commands.get(address)[0]
                    interaction_args = self.osc_bool_parameter_commands.get(address)[1]
                    self.main_queue.add(("interaction", None, (address, interaction_type, interaction_args)))
                    self.input_queue.discard(address)
            except RuntimeError:
                pass
            time.sleep(.05)

    def main_worker(self) -> None:
        while True:
            try:
                for maintask in self.main_queue:
                    match maintask[0]:
                        case "interaction":
                            self.run_phone_command(maintask[2][1], maintask[2][2])
                        case "microsip":
                            self.handle_microsip_feedback(maintask[2])
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

    def microsip_handler(self, microsip_cmd: str, caller_id: str) -> None:
        if microsip_cmd in self.microsip_state_parameters:
            prettyname =  self.microsip_state_parameters.get(microsip_cmd)[0]
            parameter = self.microsip_state_parameters.get(microsip_cmd)[1]
            self.main_queue.add(("microsip", None, (microsip_cmd, prettyname, caller_id, parameter)))

    def osc_collision(self, address: str, *args) -> None:
        if address in self.osc_bool_parameter_commands and not self.is_paused and (self.last_interaction + self.config.get_by_key("interaction_timeout")) <= time.time():
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
