from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import dearpygui.dearpygui as dpg
from flowtutor.flowchart.node import Node

from flowtutor.flowchart.whileloop import WhileLoop
from flowtutor.gui.sidebar import Sidebar

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SidebarWhileLoop(Sidebar):

    def __init__(self, gui: GUI) -> None:
        self.gui = gui
        with dpg.group(show=False) as self.main_group:
            with dpg.group():
                dpg.add_text('Condition')
                dpg.add_input_text(tag='selected_whileloop_condition',
                                   width=-1,
                                   callback=lambda _, data: (gui.selected_node.__setattr__(
                                       'condition', data),
                                       gui.redraw_all()))

    def hide(self) -> None:
        dpg.hide_item(self.main_group)

    def show(self, node: Optional[Node]) -> None:
        if not isinstance(node, WhileLoop):
            return
        self.gui.set_sidebar_title('While Loop')
        dpg.configure_item('selected_whileloop_condition', default_value=node.condition)
        dpg.show_item(self.main_group)
