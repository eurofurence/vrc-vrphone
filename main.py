import asyncio
import logging
import threading
import os
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc import udp_client
from tinyoscquery.queryservice import OSCQueryService
from tinyoscquery.utility import get_open_tcp_port, get_open_udp_port
from flask import Flask
from flask_restful import Api, Resource
from waitress import serve
from vrphone import VRPhone
from config import Config
from gui import Gui


class ReceiveCallback(Resource):
    def get(self, command, caller_id):
        vrphone.microsip_callback(microsip_cmd=command, caller_id=caller_id)
        return

    def put(self, command, caller_id):
        vrphone.microsip_callback(microsip_cmd=command, caller_id=caller_id)
        return

def start_oscquery(server_udp_port, server_tcp_port):
    def start_server():
        oscquery_server = OSCQueryService("VRC VR Phone", server_tcp_port, server_udp_port)
        oscquery_server.advertise_endpoint("/avatar")
    return start_server

def start_callbackapi() -> None:
    serve(app, host="127.0.0.1", port=19001)
    return

gui = None
try:
    cfg = Config()
    cfg.init()
    logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), './img/logo.png'))
    gui = Gui(config=cfg, window_width=550,
              window_height=1000, logo_path=logo_path)
    gui.init()
    osc_client = udp_client.SimpleUDPClient("127.0.0.1", 9000)
    vrphone = VRPhone(config=cfg, gui=gui, osc_client=osc_client)
    vrphone.init()
    dispatcher = Dispatcher()
    vrphone.map_parameters(dispatcher)

    #Callback API Init
    app = Flask(__name__)
    app.logger.setLevel(logging.ERROR)
    api = Api(app=app)
    api.add_resource(ReceiveCallback, '/<string:command>/<string:caller_id>')
    
    server_udp_port = cfg.get_by_key("server_port")

    #Start OSCQuery if active which chooses dynamic server ports for us
    if cfg.get_by_key("use_oscquery"):
        server_udp_port = get_open_udp_port()
        server_tcp_port = get_open_tcp_port()
        threading.Thread(target=start_oscquery(server_udp_port, server_tcp_port),
                         daemon=True).start()
        gui.print_terminal("OSC query started, advertising ports UDP: {} TCP: {}".format(server_udp_port, server_tcp_port))

    osc_server = ThreadingOSCUDPServer(
        ("127.0.0.1", server_udp_port), dispatcher, asyncio.new_event_loop())
    gui.print_terminal("OSC server starting on port: {}".format(server_udp_port))

    #Start OSC Thread
    threading.Thread(target=lambda: osc_server.serve_forever(2),
                     daemon=True).start()
    #Start VRPhone Thread
    threading.Thread(target=vrphone.watch,
                     daemon=True).start()
    #Start callback API
    threading.Thread(target=start_callbackapi,
                     daemon=True).start()
    gui.run()
except KeyboardInterrupt:
    print("Shutting Down...\n")
except OSError:
    pass
finally:
    if gui is not None:
        gui.cleanup()
