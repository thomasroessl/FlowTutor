import subprocess
from typing import Optional, Union
import dearpygui.dearpygui as dpg

from flowtutor.debugsession import DebugSession

LOADING_INDICATOR_TAG = 'loading_indicator'


class Debugger:

    debug_session: Optional[DebugSession] = None

    def __init__(self, parent):

        self.log_level = 0
        self._auto_scroll = True
        self.filter_id = None
        self.window_id = parent
        self.count = 0
        self.flush_count = 1000

        with dpg.group(horizontal=True, parent=self.window_id) as self.controls_group:
            self.build_button = dpg.add_image_button('hammer_image', callback=self.on_build)
            with dpg.group(horizontal=True):
                dpg.add_image_button('run_image',
                                     tag='debug_run_button',
                                     callback=self.on_debug_run,
                                     enabled=False)
                dpg.add_image_button('step_over_image',
                                     tag='debug_step_over_button',
                                     callback=self.on_debug_step_over,
                                     enabled=False)
                dpg.add_image_button('step_into_image',
                                     tag='debug_step_into_button',
                                     callback=self.on_debug_step_into,
                                     enabled=False)
                dpg.add_image_button('stop_image',
                                     tag='debug_stop_button',
                                     callback=self.on_debug_stop,
                                     enabled=False)
            with dpg.group(horizontal=True) as g1:
                dpg.add_checkbox(label='Auto-scroll', default_value=True, pos=(205, 3),
                                 callback=lambda sender: self.auto_scroll(dpg.get_value(sender)))
                dpg.add_button(label='Clear',
                               callback=lambda: dpg.delete_item(self.filter_id, children_only=True))
                with dpg.theme() as item_theme:
                    with dpg.theme_component(dpg.mvGroup):
                        dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 0.0, category=dpg.mvThemeCat_Core)
                dpg.bind_item_theme(g1, item_theme)

        self.child_id = dpg.add_child_window(parent=self.window_id, autosize_x=True, autosize_y=True)
        self.filter_id = dpg.add_filter_set(parent=self.child_id)

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

    def disable_all(self):
        self.disable_children(self.controls_group)

    def enable_build_only(self):
        self.disable_all()
        dpg.enable_item(self.build_button)

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

    def _log(self, message, level):

        if level < self.log_level:
            return

        self.count += 1

        if self.count > self.flush_count:
            self.clear_log()

        theme = None

        if level == 0:
            message = message
        elif level == 1:
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

    def log(self, message):
        self._log(message, 0)

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
        self.count = 0

    def load_start(self):
        dpg.add_loading_indicator(tag=LOADING_INDICATOR_TAG, parent=self.filter_id)
        if self._auto_scroll:
            dpg.set_y_scroll(self.child_id, -1.0)

    def load_end(self):
        dpg.delete_item(LOADING_INDICATOR_TAG)

    def on_debug_run(self):
        if self.debug_session is None:
            return
        if self.debug_session.run():
            self.log_info('Program ended.')

    def on_build(self):
        self.disable_all()
        self.load_start()
        # Build the executable
        subprocess.run(['gcc', 'flowtutor.c', '-g', '-o', 'flowtutor.exe'])
        # Start debugger
        self.debug_session = DebugSession(self)
        self.is_code_built = True
        self.load_end()
        self.log_info('Code built!')
        self.enable_all()

    def on_debug_step_over(self):
        if self.debug_session is None:
            return
        self.debug_session.next()

    def on_debug_step_into(self):
        if self.debug_session is None:
            return
        self.debug_session.step()

    def on_debug_stop(self):
        if self.debug_session is None:
            return
        self.debug_session.stop()
