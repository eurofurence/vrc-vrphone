from config import Config
from gui import Gui
import params
import subprocess

class MicroSIP:
    def __init__(self, config: Config, gui: Gui, osc_client):
        self.config = config
        self.gui = gui
        self.osc_client = osc_client
        self.call_active = False
        self.call_outgoing = False
        self.call_incoming = False
        self.microsip_state_parameters: dict[str, tuple] = {
            "cmdCallStart": ("Call started", params.call_started),
            "cmdCallEnd": ("Call ended", params.call_ended),
            "cmdIncomingCall": ("Call incoming", params.call_incoming),
            "cmdOutgoingCall": ("Call outgoing", params.call_outgoing),
            "cmdCallAnswer": ("Call answered", params.call_answered),
            "cmdCallRing": ("Phone ringing (Ring ring ring... VR Phone)", params.call_ring),
            "cmdCallBusy": ("Busy signal", params.call_busy),
        }

    def run_phone_command(self, command, args = None):
        match command:
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
                self.osc_client.send_message(parameter, True)
            case "reset":
                self.osc_client.send_message(parameter, False)
            case "resetall":
                for cmd in self.microsip_state_parameters:
                    self.osc_client.send_message(self.microsip_state_parameters.get(cmd)[1], False)
            case _:
                self.gui.print_terminal("Unknown OSC event: {}".format(tasktype))

    def call_answer(self):
        result = self.execute_microsip_command("/answer")
        return result
    
    def call_hangup(self, command = "hangupall"):
        result = self.execute_microsip_command("/" + command)
        return result

    def send_dtmf(self, code):
        result = self.execute_microsip_command("/dtmf:" + code)
        return result
    
    def call_transfer(self, number):
        result = self.execute_microsip_command("/transfer:" + number)
        return result

    def call_phonebook_entry(self, entry):
        for p, (name, number) in enumerate(self.config.get_by_key("phonebook")):
            if p == entry:
                self.gui.print_terminal(
                        "Call phone book entry #{} {} {}".format(p+1, name, number)
                )
                return self.execute_microsip_command(number)

    def execute_microsip_command(self, parameter: str):
        command = subprocess.run([self.config.get_by_key("microsip_binary"), parameter])
        return command
