from vrphone import VRPhone
from config import Config
from gui import Gui

gui = None
try:
    config = Config()
    config.init()
    gui = Gui(config=config)
    gui.init()
    vrphone = VRPhone(config=config, gui=gui)
    vrphone.run()
    gui.run()
except KeyboardInterrupt:
    print("Shutting Down...\n")
except OSError:
    pass
finally:
    if vrphone.gui is not None:
        vrphone.gui.cleanup()
