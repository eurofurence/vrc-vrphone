from config import Config
from osc import Osc
from gui import Gui
from microsip import MicroSIP
from menu import Menu

class VRPhone:
    def __init__(self, config: Config, gui: Gui):
        self.config = config
        self.gui = gui
        self.osc = Osc(config=self.config, gui=self.gui)
        self.microsip = MicroSIP(config=self.config, gui=self.gui)
        self.menu = Menu(config=self.config, gui=self.gui, osc=self.osc, microsip=self.microsip)
        self.osc.menu = self.menu

    def run(self):
        self.menu.init()
        self.gui.on_toggle_interaction_clicked.add_listener(self.osc.toggle_interactions)

