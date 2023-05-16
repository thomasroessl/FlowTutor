from __future__ import annotations
from typing import TYPE_CHECKING
import dearpygui.dearpygui as dpg

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SidebarInput:
    def __init__(self, gui: GUI) -> None:
        with dpg.group(tag='selected_input', show=False):
            with dpg.group(horizontal=True):
                dpg.add_text('Name')
                dpg.add_input_text(tag='selected_input_name',
                                   indent=50,
                                   width=-1,
                                   no_spaces=True,
                                   callback=lambda _, data: (gui.selected_node.__setattr__('var_name',
                                                                                           data),
                                                             gui.redraw_all()))
