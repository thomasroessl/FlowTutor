from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import dearpygui.dearpygui as dpg

from flowtutor.flowchart.call import Call
from flowtutor.flowchart.node import Node
from flowtutor.gui.sidebar import Sidebar

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SidebarCall(Sidebar):
    def __init__(self, gui: GUI) -> None:
        self.gui = gui
        with dpg.group(tag='selected_call', show=False) as self.main_group:
            with dpg.group():
                dpg.add_text('Expression')
                with dpg.group(horizontal=True):
                    dpg.add_input_text(tag='selected_call_expression',
                                       width=-1,
                                       callback=lambda _, data: (
                                           gui.selected_node.__setattr__('expression', data),
                                           gui.redraw_all()))
                    # dpg.add_button(label='...')

    def hide(self) -> None:
        dpg.hide_item(self.main_group)

    def show(self, node: Optional[Node]) -> None:
        if not isinstance(node, Call):
            return
        self.gui.set_sidebar_title('Call')
        dpg.configure_item('selected_call_expression', default_value=node.expression)
        dpg.show_item(self.main_group)
