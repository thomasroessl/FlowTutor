from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import dearpygui.dearpygui as dpg
from flowtutor.flowchart.assignment import Assignment
from flowtutor.flowchart.node import Node

from flowtutor.gui.sidebar import Sidebar

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SidebarAssignment(Sidebar):

    def __init__(self, gui: GUI) -> None:
        self.gui = gui
        with dpg.group(show=False) as self.main_group:
            with dpg.group(horizontal=True):
                dpg.add_text('Name')
                dpg.add_input_text(tag='selected_assignment_name',
                                   indent=50,
                                   width=-1,
                                   no_spaces=True,
                                   callback=lambda _, data: (gui.selected_node.__setattr__('var_name',
                                                                                           data),
                                                             gui.redraw_all()))

            with dpg.group(horizontal=True, tag='selected_assignment_offset_group', show=False):
                dpg.add_text('Index')
                dpg.add_input_text(tag='selected_assignment_offset',
                                   indent=50,
                                   width=-1,
                                   no_spaces=True,
                                   callback=lambda _, data: (gui.selected_node.__setattr__(
                                       'var_offset', data),
                                       gui.redraw_all()))

            with dpg.group(horizontal=True):
                dpg.add_text('Value')
                dpg.add_input_text(tag='selected_assignment_value',
                                   indent=50,
                                   width=-1,
                                   callback=lambda _, data: (gui.selected_node.__setattr__(
                                       'var_value', data),
                                       gui.redraw_all()))

    def hide(self) -> None:
        dpg.hide_item(self.main_group)

    def show(self, node: Optional[Node]) -> None:
        if not isinstance(node, Assignment):
            return
        self.gui.set_sidebar_title('Assignment')
        self.declared_variables = list(self.gui.selected_flowchart.get_all_declarations())
        dpg.configure_item('selected_assignment_name', default_value=node.var_name)
        dpg.configure_item('selected_assignment_offset', default_value=node.var_offset)
        declaration = self.gui.selected_flowchart.find_declaration(node.var_name)
        if declaration and declaration['is_array']:
            dpg.show_item('selected_assignment_offset_group')
        else:
            node.var_offset = ''
            dpg.hide_item('selected_assignment_offset_group')
        dpg.configure_item('selected_assignment_value', default_value=node.var_value)
        dpg.show_item(self.main_group)
