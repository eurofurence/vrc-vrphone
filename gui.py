import params
import config
import webbrowser
from event import Event
import dearpygui.dearpygui as dpg
from enum import Enum, auto
from time import gmtime, strftime


class Element(Enum):
    MICROSIP_BINARY = auto()
    CALL_AUTOANSWER = auto()
    PHONEBOOK = auto()
    PHONEBOOK_ENTRY_1_NAME = auto()
    PHONEBOOK_ENTRY_2_NAME = auto()
    PHONEBOOK_ENTRY_3_NAME = auto()
    PHONEBOOK_ENTRY_4_NAME = auto()
    PHONEBOOK_ENTRY_1_NUMBER = auto()
    PHONEBOOK_ENTRY_2_NUMBER = auto()
    PHONEBOOK_ENTRY_3_NUMBER = auto()
    PHONEBOOK_ENTRY_4_NUMBER = auto()
    RECEIVER_BUTTON = auto()
    CALL_STARTED = auto()
    CALL_ENDED = auto()
    CALL_INCOMING = auto()
    CALL_ANSWERED_INCOMING = auto()
    INTERACTION_TIMEOUT = auto()
    USE_OSCQUERY_CHECKBOX = auto()
    SERVER_PORT_NUMBER_INPUT = auto()
    TERMINAL_WINDOW_INPUT = auto()
    SAVE_SETTINGS_BUTTON = auto()
    CLEAR_CONSOLE_BUTTON = auto()
    TOGGLES_INTERACTIONS_BUTTON = auto()
    CONNECT_ON_STARTUP_CHECKBOX = auto()
    CONTRIBUTE_BUTTON = auto()

class Gui:
    def __init__(self, config: config.Config, window_width: int, window_height: int, logo_path: str):
        self.config = config
        self.sliders = []
        self.window_width = window_width
        self.window_height = window_height
        self.logo_path = logo_path
        self.on_save_settings_clicked = Event()
        self.on_clear_console_clicked = Event()
        self.on_toggle_interaction_clicked = Event()
        self.elements = {
            Element.MICROSIP_BINARY: None,
            Element.CALL_AUTOANSWER: None,
            Element.PHONEBOOK: None,
            Element.RECEIVER_BUTTON: None,
            Element.CALL_STARTED: None,
            Element.CALL_ENDED: None,
            Element.CALL_INCOMING: None,
            Element.CALL_ANSWERED_INCOMING: None,
            Element.INTERACTION_TIMEOUT: None,
            Element.USE_OSCQUERY_CHECKBOX: None,
            Element.SERVER_PORT_NUMBER_INPUT: None,
            Element.TERMINAL_WINDOW_INPUT: None,
            Element.SAVE_SETTINGS_BUTTON: None,
            Element.CLEAR_CONSOLE_BUTTON: None,
            Element.TOGGLES_INTERACTIONS_BUTTON: None,
            Element.CONTRIBUTE_BUTTON: None,
        }
        self.element_to_config_key = {
            Element.USE_OSCQUERY_CHECKBOX: "use_oscquery",
            Element.SERVER_PORT_NUMBER_INPUT: "server_port",
            Element.MICROSIP_BINARY: "microsip_binary",
            Element.CALL_AUTOANSWER: "call_autoanswer",
            Element.INTERACTION_TIMEOUT: "interaction_timeout",
            "buttons": {
                Element.RECEIVER_BUTTON: params.receiver_button,
            }
        }
        self.phonebook_elements = [
                {Element.PHONEBOOK_ENTRY_1_NAME: None, Element.PHONEBOOK_ENTRY_1_NUMBER: None},
                {Element.PHONEBOOK_ENTRY_2_NAME: None, Element.PHONEBOOK_ENTRY_2_NUMBER: None},
                {Element.PHONEBOOK_ENTRY_3_NAME: None, Element.PHONEBOOK_ENTRY_3_NUMBER: None},
                {Element.PHONEBOOK_ENTRY_4_NAME: None, Element.PHONEBOOK_ENTRY_4_NUMBER: None},
        ]
        self.parameter_to_button_element: dict[Element, str] = {
            value: key for key, value in self.element_to_config_key.get('buttons').items()
        }
        self.button_labels: dict[Element, str] = {
            Element.RECEIVER_BUTTON: "Receiver Button",
        }
        self.ids_to_elements = None

    def handle_save_settings_callback(self):
        self.config.write_config_to_disk()
        self.print_terminal("Settings Saved!")

    def handle_clear_console_callback(self, sender, app_data):
        self.on_clear_console_clicked.dispatch(sender, app_data)

    def handle_active_button_update(self, parameter):
        element_name = self.parameter_to_button_element.get(parameter)
        element_id = self.elements[element_name]
        existing_element_label = self.button_labels[element_name]
        result = "[" + existing_element_label + "]"
        if element_id is not None:
            dpg.configure_item(
                element_id, label=result
            )

    def handle_active_button_reset(self):
        for element_name in self.parameter_to_button_element.values():
            element_id = self.elements[element_name]
            label = self.button_labels[element_name]
            if element_id is not None:
                dpg.configure_item(
                    element_id, label=label
                )

    def handle_toggle_interactions_callback(self, sender, app_data):
        self.on_toggle_interaction_clicked.dispatch()

    def handle_input_change(self, sender, app_data):
        element = self.ids_to_elements.get(sender)
        config_key = self.element_to_config_key.get(element)
        # this implies its an intensity
        if config_key is None:
            buttons_map = self.element_to_config_key.get("buttons")
            config_key = buttons_map.get(element)
            buttons = self.config.get_by_key("buttons")
            buttons[config_key] = app_data
            self.config.update("buttons", buttons)
            return
        self.config.update(config_key, app_data)

    def handle_phonebook_change(self, sender, app_data):
        updated_element = self.ids_to_elements.get(sender)
        new_data = app_data
        phonebook = self.config.get_by_key("phonebook")
        for i, element_group in enumerate(self.phonebook_elements):
            for e, element in enumerate(element_group):
                if element == updated_element:
                    for p, (name, number) in enumerate(phonebook):
                        if p == i:
                            phonebook[i][e] = new_data
                            self.config.update("phonebook", phonebook)
                            return

    def handle_contribute_callback(self, sender, app_data):
        webbrowser.open("https://vrchat.com/home/user/usr_6a5183a0-c41a-4ef7-b69a-8ab5770fc97b")

    def create_centered_image(self, tag: str, path: str):
        image_width, image_height, _, data = dpg.load_image(path)

        with dpg.texture_registry():
            dpg.add_static_texture(
                width=image_width, height=image_height, default_value=data, tag=tag)

        spacer_width = (self.window_width - image_width) / 2
        with dpg.group(horizontal=True):
            width_spacer_id = dpg.add_spacer(width=int(spacer_width) - 25)
            dpg.add_image(tag)
            width_spacer_id_2 = dpg.add_spacer(width=int(spacer_width))

        def resize_callback():
            current_window_width = dpg.get_viewport_width()
            spacer_width = (current_window_width - image_width) / 2
            dpg.configure_item(width_spacer_id, width=int(spacer_width) - 25)
            dpg.configure_item(width_spacer_id_2, width=int(spacer_width))

        return resize_callback

    def print_terminal(self, text: str) -> None:
        value = dpg.get_value(self.elements[Element.TERMINAL_WINDOW_INPUT])
        time = strftime("%d.%m %H:%M", gmtime())
        dpg.set_value(
            self.elements[Element.TERMINAL_WINDOW_INPUT], '[' + time + '] ' + text + '\n'  + value)

    def on_clear_console(self, *args) -> None:
        dpg.set_value(
            self.elements[Element.TERMINAL_WINDOW_INPUT], "Cleared.")

    def add_listeners(self) -> None:
        self.on_clear_console_clicked.add_listener(self.on_clear_console)

    def create_microsip_binary_input(self):
        microsip_binary = self.config.get_by_key("microsip_binary") or ""
        dpg.add_text("Microsip Application Binary")
        self.elements[Element.MICROSIP_BINARY] = dpg.add_input_text(default_value=microsip_binary,
                                                                     width=-1, callback=self.handle_input_change)
    def create_interaction_timeout_input(self):
        interaction_timeout = self.config.get_by_key("interaction_timeout") or 2
        dpg.add_text("Interaction timeout")
        self.elements[Element.INTERACTION_TIMEOUT] = dpg.add_input_int(default_value=interaction_timeout,
                                                                     width=-1, callback=self.handle_input_change)
    def create_phonebook(self):
        dpg.add_text("Phonebook")
        with dpg.table(header_row=True, row_background=True,
                    borders_innerH=True, borders_outerH=True, borders_innerV=True,
                    borders_outerV=True) as table:
            dpg.add_table_column(label="Name")
            dpg.add_table_column(label="Number")
            for g, element_group in enumerate(self.phonebook_elements):
                with dpg.table_row():
                    for p, (name, number) in enumerate(self.config.get_by_key("phonebook")):
                        if g == p:
                            for e, element in enumerate(element_group):
                                if e == 0:
                                    default_value = name
                                else:
                                    default_value = number
                                self.elements[element] = dpg.add_input_text(default_value=default_value, width=-1, callback=self.handle_phonebook_change)
            self.elements[Element.PHONEBOOK] = table
            
    def create_call_autoanswer_checkbox(self):
        call_autoanswer = self.config.get_by_key("call_autoanswer")
        self.elements[Element.CALL_AUTOANSWER] = dpg.add_checkbox(
            label="Automatically Accept Calls\n(Note: This is not MicroSIP's auto accept feature)", default_value=call_autoanswer, callback=self.handle_input_change)

    def create_server_port_input(self):
        server_port = self.config.get_by_key("server_port") or 9001
        dpg.add_text("Server Port Number")
        self.elements[Element.SERVER_PORT_NUMBER_INPUT] = dpg.add_input_int(default_value=server_port,
                                                                            width=-1, callback=self.handle_input_change)

    def create_use_oscquery_checkbox(self):
        use_oscquery = self.config.get_by_key("use_oscquery")
        self.elements[Element.USE_OSCQUERY_CHECKBOX] = dpg.add_checkbox(
            label="Use OSCQuery", default_value=use_oscquery, callback=self.handle_input_change)

    def create_logs_output(self):
        dpg.add_text("Logs")
        self.elements[Element.TERMINAL_WINDOW_INPUT] = dpg.add_input_text(
            multiline=True, readonly=True, height=200, width=-1)

    def create_button_group(self):
        with dpg.group(horizontal=True):
            self.elements[Element.SAVE_SETTINGS_BUTTON] = dpg.add_button(label="Save Settings",
                                                                         callback=self.handle_save_settings_callback)
            self.elements[Element.CLEAR_CONSOLE_BUTTON] = dpg.add_button(label="Clear Console",
                                                                         callback=self.handle_clear_console_callback)
            self.elements[Element.TOGGLES_INTERACTIONS_BUTTON] = dpg.add_button(label="Toggle Interactions",
                                                                                callback=self.handle_toggle_interactions_callback)

    def create_footer(self):
        with dpg.group(width=-1):
            self.elements[Element.CONTRIBUTE_BUTTON] = dpg.add_button(
                label="\t\t\t\t  Created by Cyrus.\nThis application is not affiliated with VRChat.\n\t\t\t\t  Want to contribute?",
                width=-1,
                callback=self.handle_contribute_callback
            )

    def init(self):
        dpg.create_context()
        with dpg.window(tag="MAIN_WINDOW"):
            dpg.add_spacer(height=20)
            handle_centered_image = self.create_centered_image(
                "logo", self.logo_path)
            dpg.add_spacer(height=20)
            self.create_microsip_binary_input()
            self.create_call_autoanswer_checkbox()
            dpg.add_spacer(height=20)
            self.create_server_port_input()
            self.create_use_oscquery_checkbox()
            dpg.add_spacer(height=20)
            self.create_interaction_timeout_input()
            dpg.add_spacer(height=20)
            self.create_phonebook()
            dpg.add_spacer(height=20)
            self.create_logs_output()
            dpg.add_spacer(height=20)
            self.create_button_group()
            dpg.add_spacer(height=20)
            self.create_footer()

        self.add_listeners()
        dpg.create_viewport(title='VRChat VR Phone',
                            width=self.window_width, height=self.window_height)
        dpg.set_viewport_resize_callback(handle_centered_image)
        self.ids_to_elements = {
            value: key for key, value in self.elements.items()}
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("MAIN_WINDOW", True)

    def run(self):
        dpg.start_dearpygui()

    def cleanup(self):
        dpg.destroy_context()
