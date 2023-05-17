from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import dearpygui.dearpygui as dpg
from flowtutor.flowchart.input import Input

from flowtutor.flowchart.node import Node
from flowtutor.gui.sidebar import Sidebar

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SidebarInput(Sidebar):

    def __init__(self, gui: GUI) -> None:
        self.gui = gui
        with dpg.group(show=False) as self.main_group:
            with dpg.group(horizontal=True):
                dpg.add_text('Name')
                dpg.add_input_text(tag='selected_input_name',
                                   indent=50,
                                   width=-1,
                                   no_spaces=True,
                                   callback=lambda _, data: (gui.selected_node.__setattr__('var_name',
                                                                                           data),
                                                             gui.redraw_all()))

    def hide(self) -> None:
        dpg.hide_item(self.main_group)

    def show(self, node: Optional[Node]) -> None:
        if not isinstance(node, Input):
            return
        self.gui.set_sidebar_title('Input')
        self.declared_variables = list(self.gui.selected_flowchart.get_all_declarations())
        dpg.configure_item('selected_input_name', default_value=node.var_name)
        dpg.show_item(self.main_group)
