from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import dearpygui.dearpygui as dpg
from flowtutor.flowchart.node import Node

from flowtutor.flowchart.output import Output
from flowtutor.gui.sidebar import Sidebar

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SidebarOutput(Sidebar):

    def __init__(self, gui: GUI) -> None:
        self.gui = gui
        with dpg.group(show=False) as self.main_group:
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

    def hide(self) -> None:
        dpg.hide_item(self.main_group)

    def show(self, node: Optional[Node]) -> None:
        if not isinstance(node, Output):
            return
        self.gui.set_sidebar_title('Output')
        dpg.configure_item('selected_output_arguments', default_value=node.arguments)
        dpg.configure_item('selected_output_format_string', default_value=node.format_string)
        dpg.show_item(self.main_group)
