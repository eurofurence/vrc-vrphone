from config import Config
from osc import Osc
from gui import Gui
from microsip import MicroSIP
from menu import Menu

class VRPhone:
    def __init__(self, config: Config, gui: Gui):
        self.config = config
        self.gui = gui
        self.osc_microsip_queue: set = set()
        self.osc_vrc_queue: set = set()
        self.microsip = MicroSIP(config=self.config, gui=self.gui)
        self.osc = Osc(config=self.config, gui=self.gui, osc_microsip_queue=self.osc_microsip_queue, osc_vrc_queue=self.osc_vrc_queue)
        self.menu = Menu(config=self.config, gui=self.gui, osc=self.osc, microsip=self.microsip, osc_microsip_queue=self.osc_microsip_queue, osc_vrc_queue=self.osc_vrc_queue)
  
    def run(self):
        self.menu.run()
        self.osc.run()
        self.gui.on_toggle_interaction_clicked.add_listener(self.osc.toggle_interactions)
        self.gui.on_save_settings_clicked.add_listener(self.menu._redraw)
