from __future__ import annotations
from typing import TYPE_CHECKING
import dearpygui.dearpygui as dpg

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SidebarOutput:
    def __init__(self, gui: GUI) -> None:
        with dpg.group(tag='selected_output', show=False):
            header = dpg.add_text('Output')
            dpg.bind_item_font(header, 'header_font')
            dpg.add_separator()
            with dpg.group():
                dpg.add_input_text(tag='selected_output_format_string',
                                   width=-1,
                                   callback=lambda _, data: (gui.selected_node.__setattr__(
                                       'format_string', data),
                                       gui.redraw_all()))
            with dpg.group():
                dpg.add_text('Arguments')
                dpg.add_input_text(tag='selected_output_arguments',
                                   width=-1,
                                   callback=lambda _, data: (gui.selected_node.__setattr__(
                                       'arguments', data),
                                       gui.redraw_all()))
