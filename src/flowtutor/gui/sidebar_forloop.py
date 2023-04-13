from __future__ import annotations
from typing import TYPE_CHECKING
import dearpygui.dearpygui as dpg

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SidebarForLoop:
    def __init__(self, gui: GUI) -> None:
        with dpg.group(tag='selected_forloop', show=False):
            with dpg.group():
                dpg.add_text('Counter Variable Name')
                dpg.add_input_text(tag='selected_forloop_var_name',
                                   width=-1,
                                   no_spaces=True,
                                       callback=lambda _, data: (gui.selected_node.__setattr__(
                                           'var_name', data),
                                           gui.redraw_all()))
                dpg.add_text('Start Value')
                dpg.add_input_text(tag='selected_forloop_start_value',
                                   width=-1,
                                   no_spaces=True,
                                       callback=lambda _, data: (
                                           gui.selected_node.__setattr__('start_value', data),
                                           gui.redraw_all())
                                   )
            with dpg.group():
                dpg.add_text('Condition')
                dpg.add_input_text(tag='selected_forloop_condition',
                                   width=-1,
                                   callback=lambda _, data: (gui.selected_node.__setattr__(
                                       'condition', data),
                                       gui.redraw_all()))

            with dpg.group(horizontal=True):
                dpg.add_text('Update')
                dpg.add_input_text(tag='selected_forloop_update',
                                   width=-1,
                                   no_spaces=True,
                                   callback=lambda _, data: (gui.selected_node.__setattr__('update',
                                                                                           data),
                                                             gui.redraw_all()))
