from __future__ import annotations
from typing import TYPE_CHECKING
import dearpygui.dearpygui as dpg

from flowtutor.language import Language

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SidebarAssignment:
    def __init__(self, gui: GUI) -> None:
        with dpg.group(tag='selected_assignment', show=False):
            with dpg.group(horizontal=True):
                dpg.add_text('Name')
                dpg.add_input_text(tag='selected_assignment_name',
                                   indent=50,
                                   width=-1,
                                   no_spaces=True,
                                   callback=lambda _, data: (gui.selected_node.__setattr__('var_name',
                                                                                           data),
                                                             gui.redraw_all()))
            if Language.has_arrays():
                with dpg.group(horizontal=True, tag='selected_assignment_offset_group', show=False):
                    dpg.add_text('Index')
                    dpg.add_input_text(tag='selected_assignment_offset',
                                       indent=50,
                                       width=-1,
                                       no_spaces=True,
                                       callback=lambda _, data: (gui.selected_node.__setattr__(
                                           'var_offset', data),
                                           gui.redraw_all()))
            with dpg.group(horizontal=True):
                dpg.add_text('Value')
                dpg.add_input_text(tag='selected_assignment_value',
                                   indent=50,
                                   width=-1,
                                   callback=lambda _, data: (gui.selected_node.__setattr__(
                                       'var_value', data),
                                       gui.redraw_all()))
