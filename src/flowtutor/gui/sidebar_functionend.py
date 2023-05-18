from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import dearpygui.dearpygui as dpg
from flowtutor.flowchart.functionend import FunctionEnd
from flowtutor.flowchart.node import Node

from flowtutor.gui.sidebar import Sidebar

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SidebarFunctionEnd(Sidebar):

    def __init__(self, gui: GUI) -> None:
        self.gui = gui
        with dpg.group(tag='selected_function_end', show=False) as self.main_group:
            with dpg.group():
                dpg.add_text('Return Value')
                dpg.add_input_text(tag='selected_function_return_value',
                                   width=-1,
                                   callback=lambda _, data: (
                                       gui.selected_node.__setattr__('return_value', data),
                                       gui.redraw_all()))

    def hide(self) -> None:
        dpg.hide_item(self.main_group)

    def show(self, node: Optional[Node]) -> None:
        if not isinstance(node, FunctionEnd):
            return
        self.gui.set_sidebar_title('Function')
        dpg.configure_item('selected_function_return_value', default_value=node.return_value)
        dpg.hide_item(self.gui.section_node_extras.node_is_comment_group)
        dpg.show_item(self.main_group)
