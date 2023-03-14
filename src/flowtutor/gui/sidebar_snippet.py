from __future__ import annotations
from typing import TYPE_CHECKING
import dearpygui.dearpygui as dpg

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SidebarSnippet:
    def __init__(self, gui: GUI) -> None:
        with dpg.group(tag='selected_snippet', show=False):
            header = dpg.add_text('Code Snippet')
            dpg.bind_item_font(header, 'header_font')
            dpg.add_separator()
            dpg.add_spacer(height=5)
            with dpg.group():
                dpg.add_input_text(tag='selected_snippet_code',
                                   width=-1,
                                   height=-200,
                                   multiline=True,
                                   callback=lambda _, data: (gui.selected_node.__setattr__(
                                       'code', data),
                                       gui.redraw_all()))
