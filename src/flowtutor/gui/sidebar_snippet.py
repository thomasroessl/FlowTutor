from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import dearpygui.dearpygui as dpg
from flowtutor.flowchart.node import Node
from flowtutor.flowchart.snippet import Snippet

from flowtutor.gui.sidebar import Sidebar

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SidebarSnippet(Sidebar):
    def __init__(self, gui: GUI) -> None:
        self.gui = gui
        with dpg.group(show=False) as self.main_group:
            with dpg.group():
                dpg.add_input_text(tag='selected_snippet_code',
                                   width=-1,
                                   height=-200,
                                   multiline=True,
                                   callback=lambda _, data: (gui.selected_node.__setattr__(
                                       'code', data),
                                       gui.redraw_all()))

    def hide(self) -> None:
        dpg.hide_item(self.main_group)

    def show(self, node: Optional[Node]) -> None:
        if not isinstance(node, Snippet):
            return
        self.gui.set_sidebar_title('Code Snippet')
        dpg.configure_item('selected_snippet_code', default_value=node.code)
        dpg.show_item(self.main_group)
