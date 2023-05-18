from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import dearpygui.dearpygui as dpg

from flowtutor.flowchart.node import Node

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SectionNodeExtras:
    def __init__(self, gui: GUI) -> None:
        self.gui = gui
        with dpg.group(show=False) as self.main_group:
            dpg.add_spacer(height=5)
            dpg.add_separator()

            with dpg.group():
                dpg.add_text('Comment')
                self.node_comment = dpg.add_input_text(
                    width=-1,
                    callback=lambda _, data: (self.gui.selected_node.__setattr__('comment', data),
                                              self.gui.redraw_all()))
            with dpg.group():
                dpg.add_text('Break Point')
                self.node_break_point = dpg.add_checkbox(
                    callback=lambda _, data: (self.gui.selected_node.__setattr__('break_point', data),
                                              self.gui.redraw_all()))
            with dpg.group() as self.node_is_comment_group:
                dpg.add_text('Disabled')
                self.node_is_comment = dpg.add_checkbox(
                    callback=lambda _, data: (self.gui.selected_node.__setattr__('is_comment', data),
                                              self.gui.redraw_all()))

    def toggle(self, node: Optional[Node]) -> None:
        self.show(node) if node else self.hide()

    def hide(self) -> None:
        dpg.hide_item(self.main_group)

    def show(self, node: Node) -> None:
        dpg.show_item(self.main_group)
        dpg.show_item(self.node_is_comment_group)
        dpg.configure_item(self.node_comment, default_value=node.comment)
        dpg.configure_item(self.node_break_point, default_value=node.break_point)
        dpg.configure_item(self.node_is_comment, default_value=node.is_comment)
