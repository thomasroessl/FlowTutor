from __future__ import annotations
from typing import TYPE_CHECKING
import dearpygui.dearpygui as dpg

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SidebarCall:
    def __init__(self, gui: GUI) -> None:
        with dpg.group(tag='selected_call', show=False):
            header = dpg.add_text('Call')
            dpg.bind_item_font(header, 'header_font')
            dpg.add_separator()
            with dpg.group():
                dpg.add_text('Expression')
                with dpg.group(horizontal=True):
                    dpg.add_input_text(tag='selected_call_expression',
                                       width=-44,
                                       no_spaces=True,
                                       callback=lambda _, data: (
                                           gui.selected_node.__setattr__('expression', data),
                                           gui.redraw_all()))
                    dpg.add_button(label='...')
