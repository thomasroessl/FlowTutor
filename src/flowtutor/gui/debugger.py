from __future__ import annotations
from re import sub
from subprocess import run
from sys import stderr
from time import sleep
from typing import TYPE_CHECKING, Any, Optional, Union
import dearpygui.dearpygui as dpg
from blinker import signal
from dependency_injector.wiring import Provide, inject

from flowtutor.debugger.debugsession import DebugSession
from flowtutor.debugger.ftdbsession import FtdbSession
from flowtutor.debugger.gdbsession import GdbSession

if TYPE_CHECKING:
    from flowtutor.util_service import UtilService
    from flowtutor.flowchart.flowchart import Flowchart
    from flowtutor.language_service import LanguageService


LOADING_INDICATOR_TAG = 'loading_indicator'


class Debugger:
    '''The GUI for debugging.'''

    @inject
    def __init__(self,
                 parent: Union[str, int],
                 utils_service: UtilService = Provide['utils_service'],
                 language_service: LanguageService = Provide['language_service']) -> None:
        self.utils = utils_service
        self.language_service = language_service
        self._auto_scroll = True

        self.debug_session: Optional[DebugSession] = None
        '''The DebugSession object used for debugging.'''
        self.flowchart: Optional[Flowchart] = None
        '''The flowchart to be debugged.'''
        self.filter_id: Optional[Union[int, str]] = None
        '''The tag of the dpg filter item.'''
        self.input_id: Optional[Union[int, str]] = None
        '''The tag of the dpg input item used for user input.'''
        self.window_id: Union[int, str] = parent
        '''The tag of the parent dpg window.'''
        self.log_count = 0
        '''The number of logged lines.'''
        self.log_last_line: Optional[Union[int, str]] = None
        '''The tag of th elast log line dpg item.'''

        signal('program-finished').connect(self.on_program_finished)
        signal('program-kiled').connect(self.on_program_killed)
        signal('recieve-output').connect(self.on_recieve_output)
        signal('program-error').connect(self.on_program_error)

        with dpg.group(horizontal=True, parent=self.window_id) as self.controls_group:
            self.build_button = dpg.add_image_button('hammer_image', callback=self.on_build)

            with dpg.group(horizontal=True):
                self.run_button = dpg.add_image_button('run_image',
                                                       tag='debug_run_button',
                                                       callback=self.on_debug_run,
                                                       enabled=False)
                self.step_over_button = dpg.add_image_button('step_over_image',
                                                             tag='debug_step_over_button',
                                                             callback=self.on_debug_step_over,
                                                             enabled=False)
                self.step_into_button = dpg.add_image_button('step_into_image',
                                                             tag='debug_step_into_button',
                                                             callback=self.on_debug_step_into,
                                                             enabled=False)
                self.stop_button = dpg.add_image_button('stop_image',
                                                        tag='debug_stop_button',
                                                        callback=self.on_debug_stop,
                                                        enabled=False)
            with dpg.group(horizontal=True) as g1:
                self.auto_scroll_cb = dpg.add_checkbox(label='Auto-scroll',
                                                       default_value=True,
                                                       pos=(205, 3),
                                                       callback=lambda sender: self.auto_scroll(dpg.get_value(sender)))
                self.clear_button = dpg.add_button(label='Clear Log',
                                                   pos=(340, 0),
                                                   callback=lambda: dpg.delete_item(self.filter_id, children_only=True))
                # Set the padding of the dpg group
                with dpg.theme() as item_theme:
                    with dpg.theme_component(dpg.mvGroup):
                        dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 0.0, category=dpg.mvThemeCat_Core)
                dpg.bind_item_theme(g1, item_theme)

            # Set the paddin goof the tool buttons
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

            # Set the padding of the clear button
            with dpg.theme() as clear_button_theme:
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 12, 6, category=dpg.mvThemeCat_Core)
                with dpg.theme_component(dpg.mvButton, enabled_state=False):
                    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 5, 5, category=dpg.mvThemeCat_Core)
            dpg.bind_item_theme(self.clear_button, clear_button_theme)

        self.child_id = dpg.add_child_window(parent=self.window_id, autosize_x=True, autosize_y=True)
        self.filter_id = dpg.add_filter_set(parent=self.child_id)

        if not self.utils.is_windows:
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

    def refresh(self, flowchart: Flowchart) -> None:
        '''Refresh the GUI for the current language.

        Compiled lanuages like C get a build button, others do not.
        '''
        self.flowchart = flowchart
        if self.language_service.is_compiled(self.flowchart):
            dpg.show_item(self.build_button)
        else:
            dpg.hide_item(self.build_button)

    def on_input(self) -> None:
        '''Handle user input.'''
        input_value = dpg.get_value(self.input_id)
        if self.debug_session:
            self.debug_session.write(input_value)
        dpg.configure_item(self.input_id, default_value='')

    def disable_all(self) -> None:
        '''Diable all controls of the debugger.'''
        self.disable_children(self.controls_group)
        dpg.enable_item(self.auto_scroll_cb)
        dpg.enable_item(self.clear_button)

    def enable_build_only(self, flowchart: Flowchart) -> None:
        '''Enable only the build button. For non-compiled languages this enables the run button.

        Parameters:
            flowchart (Flowchart): The flowchart to debug.
        '''
        self.flowchart = flowchart
        self.disable_all()
        if self.language_service.is_compiled(self.flowchart):
            dpg.enable_item(self.build_button)
            dpg.show_item(self.build_button)
        else:
            dpg.enable_item(self.run_button)
            dpg.hide_item(self.build_button)

    def enable_build_and_run(self) -> None:
        '''Enables the build and run buttons.'''
        self.disable_all()
        dpg.enable_item(self.build_button)
        dpg.enable_item(self.run_button)

    def enable_all(self) -> None:
        '''Enables all controls of the debugger.'''
        self.enable_children(self.controls_group)

    def disable_children(self, item: Union[int, str]) -> None:
        '''Disables all children of a dpg item.

        Parameters:
            item (Union[int, str]): The tag of the dpg item.
        '''
        slots = dpg.get_item_children(item)
        for slot in slots.values():
            for child in slot:
                if dpg.get_item_info(child).get('type') == 'mvAppItemType::mvGroup':
                    self.disable_children(child)
                else:
                    dpg.disable_item(child)

    def enable_children(self, item: Union[int, str]) -> None:
        '''Enables all children of a dpg item.

        Parameters:
            item (Union[int, str]): The tag of the dpg item.
        '''
        slots = dpg.get_item_children(item)
        for slot in slots.values():
            for child in slot:
                if dpg.get_item_info(child).get('type') == 'mvAppItemType::mvGroup':
                    self.enable_children(child)
                else:
                    dpg.enable_item(child)

    def auto_scroll(self, value: bool) -> None:
        '''Sets if the log window should automatically scroll down for new messages.

        Parameters:
            value (bool): True if auto scrolling is on.
        '''
        self._auto_scroll = value

    def _log(self, message: str, level: int) -> None:
        '''Logs the message in the logger window.

        Parameters:
            message (str): The message to dispaly.
            level (int): The log level of the message.
        '''

        if self.log_count > 1000:
            self.clear_log()

        theme = None
        # For log-level 0 the messages are processed per character
        # For all other levels the message is processed per line
        if level == 0:
            if not self.log_last_line:
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
            if theme:
                dpg.bind_item_theme(new_log, theme)

        if self._auto_scroll:
            dpg.set_y_scroll(self.child_id, -1.0)

    def log(self, character: str) -> None:
        '''Logs the character in the logger window.

        Parameters:
            character (str): The character to display.
        '''
        self._log(character, 0)

    def log_debug(self, message: str) -> None:
        '''Logs the message in the logger window in DEBUG style.

        Parameters:
            message (str): The message to display.
        '''
        self._log(message, 1)

    def log_info(self, message: str) -> None:
        '''Logs the message in the logger window in INFO style.

        Parameters:
            message (str): The message to display.
        '''
        self._log(message, 2)

    def log_warning(self, message: str) -> None:
        '''Logs the message in the logger window in WARNING style.

        Parameters:
            message (str): The message to display.
        '''
        self._log(message, 3)

    def log_error(self, message: str) -> None:
        '''Logs the message in the logger window in ERROR style.

        Parameters:
            message (str): The message to display.
        '''
        self._log(message, 4)

    def clear_log(self) -> None:
        '''Clears the logger window of a ll messages.'''
        dpg.delete_item(self.filter_id, children_only=True)
        self.log_count = 0

    def load_start(self) -> None:
        '''Shows a loading indicator.'''
        dpg.add_loading_indicator(tag=LOADING_INDICATOR_TAG, parent=self.filter_id)
        if self._auto_scroll:
            dpg.set_y_scroll(self.child_id, -1.0)

    def load_end(self) -> None:
        '''Removes the loading indicator.'''
        dpg.delete_item(LOADING_INDICATOR_TAG)

    def on_debug_run(self) -> None:
        '''Starts the debugger and runs the program.'''
        if self.flowchart:
            if not self.debug_session:
                # Start debugger
                if self.flowchart.lang_data['debugger'] == 'pdb':
                    self.debug_session = FtdbSession(self)
                else:
                    self.debug_session = GdbSession(self)
                self.debug_session.run(self.flowchart)
            else:
                self.debug_session.cont(self.flowchart)

    def on_build(self) -> None:
        '''Compiles the C program using GCC.'''
        self.disable_all()
        self.load_start()

        try:
            gcc_exe = self.utils.get_gcc_exe()
        except FileNotFoundError as error:
            self.log_error(str(error))
            self.load_end()
            return

        print(gcc_exe, file=stderr)

        # Build the executable
        result = run([
            gcc_exe,
            self.utils.get_source_path('.c'),
            '-g',
            '-o',
            self.utils.get_exe_path(),
            '-lm'],
            capture_output=True)

        output = '\n'.join(filter(lambda s: s, [result.stdout.decode('utf-8'), result.stderr.decode('utf-8')]))
        output_lines = output.split('\n')

        log = self.log_info
        for line in output_lines:
            output_line = sub(r'.*?:(\d+:\d+:)?', '', line, count=1)
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

    def on_debug_step_over(self) -> None:
        '''Excecute a single step of the program, stepping over functions.'''
        if not self.debug_session or not self.flowchart:
            return
        self.debug_session.next(self.flowchart)

    def on_debug_step_into(self) -> None:
        '''Excecute a single step of the program, stepping into functions.'''
        if not self.debug_session or not self.flowchart:
            return
        self.debug_session.step(self.flowchart)

    def on_debug_stop(self) -> None:
        '''Stop execution of the program.'''
        if not self.debug_session:
            return
        self.debug_session.stop()

    def on_program_finished(self, _: Any, **kw: Any) -> None:
        '''Log a message after program has finished'''
        sleep(0.3)
        self.log_info('Program ended.')
        self.debug_session = None

    def on_program_error(self, _: Any, **kw: str) -> None:
        '''Log a message on program errors.'''
        error = kw['error']
        self.log_error(error)

    def on_program_killed(self, _: Any, **kw: Any) -> None:
        '''Log a message if the program gets killed.'''
        self.log_info('Program killed.')
        self.debug_session = None

    def on_recieve_output(self, _: Any, **kw: str) -> None:
        '''Log outputs to the logger window.'''
        output = kw['output']
        self.log(output)
