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
        self.osc_parameters: dict[str, str] = {
            params.call_answer: "/answer",
            params.call_start: self.config.get_by_key("call_menu_number"),
        }
        # start, duration, parameters
        self.active_hit: None | tuple[float, float, list[self.osc_parameters]] = None
        self.interactions_to_parameters: dict[str, str] = {
            value: key for key, value in self.osc_parameters.items()}
        self.is_paused = False

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
                self.gui.handle_active_interaction_reset()

                if self.active_hit:
                    if ((self.active_hit[0] + self.active_hit[1]) < time.time()):
                        self.active_hit = None
                    else:
                        time.sleep(.05)
                        continue

                if len(self.active_interactions) > 0 and not self.is_paused:
                    interactions = []
                    for interaction in self.active_interactions:
                        parameter = self.interactions_to_parameters.get(interaction)
                        self.gui.handle_active_interaction_update(
                            parameter=parameter)
                        interactions.append(interaction)
                    if len(interactions) > 0:
                        self.gui.print_terminal(
                            "Running Microsip Command: {}".format(interaction))
                        self.execute_microsip_command(interaction)

            except RuntimeError:  # race condition for set changing during iteration
                pass
            time.sleep(.05)

    def on_collission_enter(self, address: str, *args) -> None:
        if address in self.osc_parameters:
            if len(args) != 1:
                return
            was_entered: bool = args[0]
            if type(was_entered) != bool:
                return
            interaction = self.osc_parameters.get(address)
            if was_entered:
                self.active_interactions.add(interaction)
            else:
                self.active_interactions.discard(interaction)

    def map_parameters(self, dispatcher: dispatcher.Dispatcher) -> None:
        dispatcher.set_default_handler(self.on_collission_enter)

    def init(self) -> None:
        self.gui.on_toggle_interaction_clicked.add_listener(
            self.toggle_interactions)
