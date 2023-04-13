from __future__ import annotations
from typing import TYPE_CHECKING
import dearpygui.dearpygui as dpg

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SidebarFunctionEnd:
    def __init__(self, gui: GUI) -> None:
        with dpg.group(tag='selected_function_end', show=False):
            with dpg.group():
                dpg.add_text('Return Value')
                dpg.add_input_text(tag='selected_function_return_value',
                                   width=-1,
                                   no_spaces=True,
                                   callback=lambda _, data: (
                                       gui.selected_node.__setattr__('return_value', data),
                                       gui.redraw_all()))
