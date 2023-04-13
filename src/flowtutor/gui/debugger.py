import re
import subprocess
import sys
from typing import Optional, Union
import dearpygui.dearpygui as dpg
from blinker import signal
from dependency_injector.wiring import Provide, inject

from flowtutor.util_service import UtilService
from flowtutor.debugsession import DebugSession

LOADING_INDICATOR_TAG = 'loading_indicator'


class Debugger:

    debug_session: Optional[DebugSession] = None

    @inject
    def __init__(self, parent, utils_service: UtilService = Provide['utils_service']):

        self.utils = utils_service

        self.log_level = 0
        self._auto_scroll = True
        self.filter_id = None
        self.input_id = None
        self.window_id = parent
        self.log_count = 0
        self.log_flush_count = 1000
        self.log_last_line: Optional[Union[int, str]] = None

        signal('program-finished').connect(self.on_program_finished)
        signal('program-kiled').connect(self.on_program_killed)
        signal('recieve_output').connect(self.on_recieve_output)
        signal('program-error').connect(self.on_program_error)

        with dpg.group(horizontal=True, parent=self.window_id) as self.controls_group:
            self.build_button = dpg.add_image_button('hammer_image', callback=lambda: self.on_build(self))

            with dpg.group(horizontal=True):
                self.run_button = dpg.add_image_button('run_image',
                                                       tag='debug_run_button',
                                                       callback=lambda: self.on_debug_run(self),
                                                       enabled=False)
                self.step_over_button = dpg.add_image_button('step_over_image',
                                                             tag='debug_step_over_button',
                                                             callback=lambda: self.on_debug_step_over(self),
                                                             enabled=False)
                self.step_into_button = dpg.add_image_button('step_into_image',
                                                             tag='debug_step_into_button',
                                                             callback=lambda: self.on_debug_step_into(self),
                                                             enabled=False)
                self.stop_button = dpg.add_image_button('stop_image',
                                                        tag='debug_stop_button',
                                                        callback=lambda: self.on_debug_stop(self),
                                                        enabled=False)
            with dpg.group(horizontal=True) as g1:
                self.auto_scroll_cb = dpg.add_checkbox(label='Auto-scroll',
                                                       default_value=True,
                                                       pos=(205, 3),
                                                       callback=lambda sender: self.auto_scroll(dpg.get_value(sender)))
                self.clear_button = dpg.add_button(label='Clear',
                                                   pos=(340, 0),
                                                   callback=lambda: dpg.delete_item(self.filter_id, children_only=True))
                with dpg.theme() as item_theme:
                    with dpg.theme_component(dpg.mvGroup):
                        dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 0.0, category=dpg.mvThemeCat_Core)
                dpg.bind_item_theme(g1, item_theme)

            with dpg.theme() as tool_button_theme:
                with dpg.theme_component(dpg.mvImageButton):
                    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 5, 5, category=dpg.mvThemeCat_Core)
                with dpg.theme_component(dpg.mvImageButton, enabled_state=False):
                    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 5, 5, category=dpg.mvThemeCat_Core)

            dpg.bind_item_theme(self.build_button, tool_button_theme)
            dpg.bind_item_theme(self.run_button, tool_button_theme)
            dpg.bind_item_theme(self.step_over_button, tool_button_theme)
            dpg.bind_item_theme(self.step_into_button, tool_button_theme)
            dpg.bind_item_theme(self.stop_button, tool_button_theme)

            with dpg.theme() as clear_button_theme:
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 12, 6, category=dpg.mvThemeCat_Core)
                with dpg.theme_component(dpg.mvButton, enabled_state=False):
                    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 5, 5, category=dpg.mvThemeCat_Core)

            dpg.bind_item_theme(self.clear_button, clear_button_theme)

        self.child_id = dpg.add_child_window(parent=self.window_id, autosize_x=True, autosize_y=True)
        self.filter_id = dpg.add_filter_set(parent=self.child_id)

        if True:
            dpg.configure_item(self.child_id, autosize_y=False, height=190)

            input_window_id = dpg.add_child_window(parent=self.window_id, autosize_x=True, height=22)

            with dpg.theme() as test:
                with dpg.theme_component(dpg.mvChildWindow):
                    dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0.0, category=dpg.mvThemeCat_Core)
            dpg.bind_item_theme(input_window_id, test)

            with dpg.group(horizontal=True, parent=input_window_id):
                self.input_id = dpg.add_input_text(width=-80, on_enter=True, callback=self.on_input)
                dpg.add_button(label='Enter', width=71, callback=self.on_input)

        with dpg.theme() as self.debug_theme:
            with dpg.theme_component(0):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (64, 128, 255, 255))

        with dpg.theme() as self.info_theme:
            with dpg.theme_component(0):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (64, 128, 255, 255))

        with dpg.theme() as self.warning_theme:
            with dpg.theme_component(0):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 191, 0, 255))

        with dpg.theme() as self.error_theme:
            with dpg.theme_component(0):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 0, 0, 255))

    def on_input(self):
        self.utils.write_tty(dpg.get_value(self.input_id))
        dpg.configure_item(self.input_id, default_value='')

    def disable_all(self):
        self.disable_children(self.controls_group)
        dpg.enable_item(self.auto_scroll_cb)
        dpg.enable_item(self.clear_button)

    def enable_build_only(self):
        self.disable_all()
        dpg.enable_item(self.build_button)

    def enable_build_and_run(self):
        self.disable_all()
        dpg.enable_item(self.build_button)
        dpg.enable_item(self.run_button)

    def enable_all(self):
        self.enable_children(self.controls_group)

    def disable_children(self, item: Union[int, str]):
        slots = dpg.get_item_children(item)
        for slot in slots.values():
            for child in slot:
                if dpg.get_item_info(child).get('type') == 'mvAppItemType::mvGroup':
                    self.disable_children(child)
                else:
                    dpg.disable_item(child)

    def enable_children(self, item: Union[int, str]):
        slots = dpg.get_item_children(item)
        for slot in slots.values():
            for child in slot:
                if dpg.get_item_info(child).get('type') == 'mvAppItemType::mvGroup':
                    self.enable_children(child)
                else:
                    dpg.enable_item(child)

    def auto_scroll(self, value):
        self._auto_scroll = value

    def _log(self, message: str, level):

        if level < self.log_level:
            return

        if self.log_count > self.log_flush_count:
            self.clear_log()

        theme = None
        # For log-level 0 the messages are processed per character
        # For all other levels the message is processed per line
        if level == 0:
            if self.log_last_line is None:
                self.log_last_line = dpg.add_text(message, parent=self.filter_id, filter_key=message)
            else:
                line_value = dpg.get_value(self.log_last_line)
                dpg.configure_item(self.log_last_line, default_value=line_value + message)
            if message.endswith('\n'):
                self.log_last_line = None
        else:
            self.log_last_line = None
            self.log_count += 1
            if level == 1:
                message = '[DEBUG]  \t' + message
                theme = self.debug_theme
            elif level == 2:
                message = '[INFO]   \t' + message
                theme = self.info_theme
            elif level == 3:
                message = '[WARNING]\t' + message
                theme = self.warning_theme
            elif level == 4:
                message = '[ERROR]  \t' + message
                theme = self.error_theme
            new_log = dpg.add_text(message, parent=self.filter_id, filter_key=message)
            if theme is not None:
                dpg.bind_item_theme(new_log, theme)

        if self._auto_scroll:
            dpg.set_y_scroll(self.child_id, -1.0)

    def log(self, character):
        self._log(character, 0)

    def log_debug(self, message):
        self._log(message, 1)

    def log_info(self, message):
        self._log(message, 2)

    def log_warning(self, message):
        self._log(message, 3)

    def log_error(self, message):
        self._log(message, 4)

    def clear_log(self):
        dpg.delete_item(self.filter_id, children_only=True)
        self.log_count = 0

    def load_start(self):
        dpg.add_loading_indicator(tag=LOADING_INDICATOR_TAG, parent=self.filter_id)
        if self._auto_scroll:
            dpg.set_y_scroll(self.child_id, -1.0)

    def load_end(self):
        dpg.delete_item(LOADING_INDICATOR_TAG)

    @staticmethod
    def on_debug_run(self):
        if self.debug_session is None:
            # Start debugger
            self.debug_session = DebugSession(self)
            self.debug_session.run()
        else:
            self.debug_session.cont()

    @staticmethod
    def on_build(self):
        self.disable_all()
        self.load_start()

        gcc_exe = self.utils.get_gcc_exe()
        print(gcc_exe, file=sys.stderr)

        # Build the executable
        result = subprocess.run([
            gcc_exe,
            self.utils.get_c_source_path(),
            '-g',
            '-o',
            self.utils.get_exe_path(),
            '-lm'],
            capture_output=True)

        output = '\n'.join(filter(lambda s: s, [result.stdout.decode('utf-8'), result.stderr.decode('utf-8')]))
        output_lines = output.split('\n')

        log = self.log_info
        for line in output_lines:
            output_line = re.sub(r'.*?:(\d+:\d+:)?', '', line, count=1)
            stripped = output_line.lstrip()
            if stripped.startswith('warning'):
                log = self.log_warning
            elif stripped.startswith('error'):
                log = self.log_error
            elif stripped.startswith('note'):
                log = self.log_info
            if len(stripped) > 0:
                log(output_line)

        if result.returncode == 0:
            self.is_code_built = True
            self.log_info('Code built!')
            self.enable_build_and_run()

        self.load_end()

    @staticmethod
    def on_debug_step_over(self):
        if self.debug_session is None:
            return
        self.debug_session.next()

    @staticmethod
    def on_debug_step_into(self):
        if self.debug_session is None:
            return
        self.debug_session.step()

    @staticmethod
    def on_debug_stop(self):
        if self.debug_session is None:
            return
        self.debug_session.stop()

    def on_program_finished(self, _, **kw):
        self.log_info('Program ended.')
        self.debug_session = None

    def on_program_error(self, _, **kw):
        error = kw['error']
        self.log_error(error)

    def on_program_killed(self, _, **kw):
        self.log_info('Program killed.')
        self.debug_session = None

    def on_recieve_output(self, _, **kw):
        output = kw['output']
        self.log(output)
