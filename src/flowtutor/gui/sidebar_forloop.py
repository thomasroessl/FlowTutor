from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import dearpygui.dearpygui as dpg

from flowtutor.flowchart.forloop import ForLoop
from flowtutor.flowchart.node import Node
from flowtutor.gui.sidebar import Sidebar

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SidebarForLoop(Sidebar):

    def __init__(self, gui: GUI) -> None:
        self.gui = gui
        with dpg.group(show=False) as self.main_group:
            with dpg.group():
                dpg.add_text('Counter Variable Name')
                dpg.add_input_text(tag='selected_forloop_var_name',
                                   width=-1,
                                   no_spaces=True,
                                       callback=lambda _, data: (gui.selected_node.__setattr__(
                                           'var_name', data),
                                           gui.redraw_all()))
                dpg.add_text('Start Value')
                dpg.add_input_text(tag='selected_forloop_start_value',
                                   width=-1,
                                   no_spaces=True,
                                       callback=lambda _, data: (
                                           gui.selected_node.__setattr__('start_value', data),
                                           gui.redraw_all())
                                   )
            with dpg.group():
                dpg.add_text('Condition')
                dpg.add_input_text(tag='selected_forloop_condition',
                                   width=-1,
                                   callback=lambda _, data: (gui.selected_node.__setattr__(
                                       'condition', data),
                                       gui.redraw_all()))

            with dpg.group(horizontal=True):
                dpg.add_text('Update')
                dpg.add_input_text(tag='selected_forloop_update',
                                   width=-1,
                                   callback=lambda _, data: (gui.selected_node.__setattr__('update',
                                                                                           data),
                                                             gui.redraw_all()))

    def hide(self) -> None:
        dpg.hide_item(self.main_group)

    def show(self, node: Optional[Node]) -> None:
        if not isinstance(node, ForLoop):
            return
        self.gui.set_sidebar_title('For Loop')
        dpg.configure_item('selected_forloop_condition', default_value=node.condition)
        dpg.configure_item('selected_forloop_var_name', default_value=node.var_name)
        dpg.configure_item('selected_forloop_start_value', default_value=node.start_value)
        dpg.configure_item('selected_forloop_update', default_value=node.update)
        dpg.show_item(self.main_group)
