# pyright: reportMissingImports=false
from pythonosc import dispatcher
from config import Config
from gui import Gui
import params
import time
import subprocess

class VRPhone:
    def __init__(self, config: Config, gui: Gui):
        self.config = config
        self.gui = gui
        self.active_interactions: set = set()
        self.call_active = False
        self.is_paused = False
        self.osc_input_parameters: dict[str, tuple] = {
            params.call_answer_button: ("answerbutton", None),
            params.phonebook_entry_1_button: ("phonebook", 1),
            params.phonebook_entry_2_button: ("phonebook", 2),
            params.phonebook_entry_3_button: ("phonebook", 3),
            params.phonebook_entry_4_button: ("phonebook", 4)
        }
        self.parameters_to_types: dict[str, tuple] = {
            value: key for key, value in self.osc_input_parameters.items()}

    def handle_answer_button(self):
        if self.call_active:
            self.gui.print_terminal(
                "Call hangup"
            )
            command = "/hangupall"
        else:
            self.gui.print_terminal(
                "Call answered"
            )
            command = "/answer"
        self.call_active = not self.call_active
        return self.execute_microsip_command(command)

    def handle_phonebook_entry(self, entry):
        if not self.call_active:
            for p, (name, number) in enumerate(self.config.get_by_key("phonebook").items()):
                if p == entry:
                    self.gui.print_terminal(
                            "Call phone book entry #{} {} {}".format(p, name, number)
                    )
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
        #command = subprocess.run([microsip_binary, parameter])
        command = True
        return command

    def watch(self) -> None:
        while True:
            try:
                self.gui.handle_active_button_reset()
                if len(self.active_interactions) > 0 and not self.is_paused:
                    commands = []
                    for interaction in self.active_interactions:
                        interaction_type = self.osc_input_parameters.get(interaction)[0]
                        interaction_args = self.osc_input_parameters.get(interaction)[1]
                        if interaction_type == "answerbutton" or interaction_type == "button":
                            self.gui.handle_active_button_update(
                                parameter=interaction)
                        commands.append((interaction, interaction_type, interaction_args))
                    if len(commands) > 0:
                        for command in commands:
                            interaction = command[0]
                            interaction_type = command[1]
                            interaction_args = command[2]
                            match interaction_type:
                                case "answerbutton":
                                    self.handle_answer_button()                               
                                case "phonebook":
                                    self.handle_phonebook_entry(interaction_args)
                                case _:
                                    self.gui.print_terminal("Unknown type?")
                            time.sleep(self.config.get_by_key("interaction_timeout"))
            except RuntimeError:  # race condition for set changing during iteration
                pass
            time.sleep(.05)

    def on_collission_enter(self, address: str, *args) -> None:
        if address in self.osc_input_parameters:
            if len(args) != 1:
                return
            was_entered: bool = args[0]
            if type(was_entered) != bool:
                return
            if was_entered:
                self.active_interactions.add(address)
            else:
                self.active_interactions.discard(address)

    def map_parameters(self, dispatcher: dispatcher.Dispatcher) -> None:
        dispatcher.set_default_handler(self.on_collission_enter)

    def init(self) -> None:
        self.gui.on_toggle_interaction_clicked.add_listener(
            self.toggle_interactions)
