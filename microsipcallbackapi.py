from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import params
from config import Config
from gui import Gui

class MicroSIPCallbackAPI():
    def __init__(self, config: Config, gui: Gui, oscclient ):
        self.config = config
        self.oscclient = oscclient
        self.gui = gui
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.osc_output_parameters: dict[str, tuple] = {
            params.call_started: ("started", None),
            params.call_ended: ("ended", 1),
            params.call_incoming: ("incoming", 2),
            params.call_answered_incoming: ("answered", 3)
        }
        self.api.add_resource(ReceiveCallback, '/<string:command>/<string:caller_id>')

class ReceiveCallback(Resource):
    def get(self, command, caller_id):
        return
        #todo
        #return {: todos[todo_id]}

    def put(self, command, caller_id):
        return
        #todo
        #return {todo_id: todos[todo_id]}
