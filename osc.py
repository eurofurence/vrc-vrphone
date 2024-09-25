from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc import udp_client
from config import Config
from gui import Gui
import params
import time
import asyncio
import threading

class Osc:
    def __init__(self, config: Config, gui: Gui, osc_vrc_queue: set = set(), osc_microsip_queue: set = set()):
        self.config = config
        self.gui = gui
        self.osc_microsip_queue = osc_microsip_queue
        self.osc_vrc_queue = osc_vrc_queue
        self.last_interaction = time.time() - self.config.get_by_key("interaction_timeout")
        self.is_paused = False
        dispatcher = Dispatcher()
        self.map_parameters(dispatcher)
        server_udp_port = self.config.get_by_key("server_port")
        self.server = ThreadingOSCUDPServer(("127.0.0.1", server_udp_port), dispatcher, asyncio.new_event_loop())
        self.client = udp_client.SimpleUDPClient("127.0.0.1", 9000)
        self.gui.print_terminal("OSC server starting on port: {}".format(server_udp_port))
        self.avatar_change_input = params.avatar_change
        self.microsip_callback_adresses: list[str] = [
            params.microsip_call_outgoing,
            params.microsip_call_incoming,
            params.microsip_call_ring,
            params.microsip_call_answer,
            params.microsip_call_answer,
            params.microsip_call_busy,
            params.microsip_call_start,
            params.microsip_call_end,
        ]
        self.vrc_bool_inputs: list[str] = [
            params.keypad_button,
            params.center_button,
            params.ok_button,
            params.cancel_button,
            params.yes_button,
            params.no_button
        ]

    def osc_handler(self, address: str, *args):
        if address in self.microsip_callback_adresses:
            if len(args) != 1:
                caller = None
            else:
                caller = int(args[0])
            if address not in self.osc_microsip_queue:
                self.osc_microsip_queue.add((address, caller))
                return
        if address == self.avatar_change_input:
            self.osc_vrc_queue.add(address)
            return
        if not self.is_paused:
            if address in self.vrc_bool_inputs:
                if self.last_interaction + self.config.get_by_key("interaction_timeout") > time.time():
                    return
                if len(args) != 1:
                    return
                was_entered: bool = args[0]
                if type(was_entered) != bool:
                    return
                if was_entered and address not in self.osc_vrc_queue:
                    self.osc_vrc_queue.add(address)
                    self.last_interaction = time.time()

    def map_parameters(self, dispatcher: Dispatcher):
        dispatcher.set_default_handler(self.osc_handler)

    def toggle_interactions(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.gui.print_terminal(
                "Interactions Paused.")
        else:
            self.gui.print_terminal(
                "Interactions Continued.")

    def run(self):
        threading.Thread(target=lambda: self.server.serve_forever(2), daemon=True).start()
