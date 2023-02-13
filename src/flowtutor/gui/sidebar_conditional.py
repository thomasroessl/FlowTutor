from __future__ import annotations
from typing import TYPE_CHECKING
import dearpygui.dearpygui as dpg

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SidebarConditional:
    def __init__(self, gui: GUI) -> None:
        with dpg.group(tag='selected_conditional', show=False):
            header = dpg.add_text('Conditional')
            dpg.bind_item_font(header, 'header_font')
            dpg.add_separator()
            with dpg.group():
                dpg.add_text('Condition')
                dpg.add_input_text(tag='selected_conditional_condition',
                                   width=-1,
                                   callback=lambda _, data: (gui.selected_node.__setattr__(
                                       'condition', data),
                                       gui.redraw_all()))
