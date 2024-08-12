from config import Config
from gui import Gui
import subprocess

class MicroSIP:
    def __init__(self, config: Config, gui: Gui):
        self.config = config
        self.gui = gui

    def run_phone_command(self, command, args = None):
        self.gui.print_terminal("Microsip: Running command: {} args: {}".format(command, args)) if self.config.get_by_key("log_verbose") else None
        match command:
            case "answer":
                self.gui.print_terminal("Microsip: Answering call")
                self.call_answer()
            case "hangup":
                self.gui.print_terminal("Microsip: Hangup call")
                self.call_hangup()
            case "hangupcalling":
                self.gui.print_terminal("Microsip: Hangup outgoing call")
                self.call_hangup(command)
            case "hangupincoming":
                self.gui.print_terminal("Microsip: Hangup incoming call")
                self.call_hangup(command)
            case "phonebook":
                self.gui.print_terminal("Microsip: Call phonebook entry #{}".format(args+1))
                self.call_phonebook_entry(args)
            case "dtmf":
                self.gui.print_terminal("Microsip: Send DTMF sequence: {}".format(args))
                self.send_dtmf(args)
            case "transfer":
                self.gui.print_terminal("Microsip: Transfer call to: {}".format(args))
                self.call_transfer(args)

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
                return self.execute_microsip_command(number)

    def execute_microsip_command(self, parameter: str):
        command = subprocess.run([self.config.get_by_key("microsip_binary"), parameter])
        return command
