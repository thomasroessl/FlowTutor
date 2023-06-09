from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union
import dearpygui.dearpygui as dpg
from flowtutor.flowchart.node import Node
from flowtutor.flowchart.template import Template

from flowtutor.gui.sidebar import Sidebar

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SidebarTemplate(Sidebar):
    def __init__(self, gui: GUI) -> None:
        self.gui = gui
        self.main_group = dpg.add_group(show=False)
        self.input_groups: list[Union[int, str]] = []

    def hide(self) -> None:
        for input in self.input_groups:
            dpg.delete_item(input)
        self.input_groups.clear()
        dpg.hide_item(self.main_group)

    def show(self, node: Optional[Node]) -> None:
        if not isinstance(node, Template):
            return
        self.gui.set_sidebar_title(node.data['label'])

        with dpg.group(parent=self.main_group):
            for parameter in node.parameters:
                with dpg.group(horizontal=True) as input_group:
                    dpg.add_text(parameter['label'])
                    if 'options' in parameter:
                        dpg.add_combo(parameter['options'],
                                      width=-1,
                                      default_value=node.values.__getitem__(parameter['name']) or '',
                                      user_data=parameter,
                                      callback=lambda s, data:
                                      (node.values.__setitem__(dpg.get_item_user_data(s)['name'], data),
                                       self.gui.redraw_all()))
                    else:
                        dpg.add_input_text(width=-1,
                                           default_value=node.values.__getitem__(parameter['name']) or '',
                                           user_data=parameter,
                                           callback=lambda s, data:
                                           (node.values.__setitem__(dpg.get_item_user_data(s)['name'], data),
                                            self.gui.redraw_all()))
                self.input_groups.append(input_group)

        dpg.show_item(self.main_group)
