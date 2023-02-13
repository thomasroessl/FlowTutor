from __future__ import annotations
from typing import TYPE_CHECKING
import dearpygui.dearpygui as dpg

from flowtutor.language import Language

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SidebarLoop:
    def __init__(self, gui: GUI) -> None:
        with dpg.group(tag='selected_loop', show=False):
            header = dpg.add_text('Loop')
            dpg.bind_item_font(header, 'header_font')
            dpg.add_separator()
            dpg.add_spacer(height=5)
            if Language.has_for_loops():
                with dpg.group(horizontal=True):
                    dpg.add_text('Type')
                    dpg.add_combo(Language.get_loop_types(),
                                  tag='selected_loop_type',
                                  indent=50,
                                  width=-1,
                                  callback=lambda _, data: (gui.selected_node.__setattr__(
                                      'loop_type', data),
                                      gui.on_select_node(gui.selected_node),
                                      gui.redraw_all()))
                with dpg.group(tag='selected_for_loop_group_1'):
                    dpg.add_text('Counter Variable Name')
                    dpg.add_input_text(tag='selected_loop_var_name',
                                       width=-1,
                                       no_spaces=True,
                                           callback=lambda _, data: (gui.selected_node.__setattr__(
                                               'var_name', data),
                                               gui.redraw_all()))
                    dpg.add_text('Start Value')
                    dpg.add_input_text(tag='selected_loop_start_value',
                                       width=-1,
                                       no_spaces=True,
                                           callback=lambda _, data: (
                                               gui.selected_node.__setattr__('start_value', data),
                                               gui.redraw_all())
                                       )
            with dpg.group():
                dpg.add_text('Condition')
                dpg.add_input_text(tag='selected_loop_condition',
                                   width=-1,
                                   callback=lambda _, data: (gui.selected_node.__setattr__(
                                       'condition', data),
                                       gui.redraw_all()))
            if Language.has_for_loops():
                with dpg.group(horizontal=True, tag='selected_for_loop_group_2'):
                    dpg.add_text('Update')
                    dpg.add_input_text(tag='selected_loop_update',
                                       width=-1,
                                       no_spaces=True,
                                       callback=lambda _, data: (gui.selected_node.__setattr__('update',
                                                                                               data),
                                                                 gui.redraw_all()))
