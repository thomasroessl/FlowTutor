from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import dearpygui.dearpygui as dpg
from flowtutor.flowchart.declarations import Declarations
from flowtutor.flowchart.node import Node
from flowtutor.gui.sidebar import Sidebar
from flowtutor.language import Language

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SidebarDeclarations(Sidebar):

    def __init__(self, gui: GUI) -> None:
        self.gui = gui
        self.main_group = dpg.add_group(show=False)

    def refresh(self) -> None:
        for child in dpg.get_item_children(self.main_group)[1]:
            dpg.delete_item(child)

        if isinstance(self.gui.selected_node, Declarations):
            with dpg.theme() as delete_button_theme:
                with dpg.theme_component(dpg.mvImageButton):
                    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 3, 3, category=dpg.mvThemeCat_Core)
            for [i, declaration] in enumerate(self.gui.selected_node.declarations):
                if i > 0:
                    dpg.add_spacer(height=5, parent=self.main_group)
                with dpg.group(horizontal=True, parent=self.main_group):
                    dpg.add_text('Name')
                    dpg.add_input_text(tag=f'selected_declaration[{i}]_name',
                                       indent=50,
                                       width=-33 if i > 0 else -1,
                                       no_spaces=True,
                                       default_value=declaration['var_name'],
                                       user_data=i,
                                       callback=lambda s, data: (
                                           self.gui.selected_node.declarations[dpg.get_item_user_data(s)]
                                           .update({'var_name': data}),
                                           self.gui.redraw_all()))
                    if i > 0:
                        delete_button = dpg.add_image_button(
                            'trash_image', height=18, width=18, user_data=i,
                            callback=lambda s: self.on_delete_declaration(dpg.get_item_user_data(s)))
                        dpg.bind_item_theme(delete_button, delete_button_theme)
                with dpg.group(horizontal=True, parent=self.main_group):
                    dpg.add_text('Type')
                    dpg.add_combo(Language.get_data_types(self.gui.flowcharts['main']),
                                  tag=f'selected_declaration[{i}]_type',
                                  indent=50,
                                  width=-1,
                                  default_value=declaration['var_type'],
                                  user_data=i,
                                  callback=lambda s, data: (
                        self.gui.selected_node.declarations[dpg.get_item_user_data(s)].update({'var_type': data}),
                        self.gui.redraw_all()))

                with dpg.group(horizontal=True, parent=self.main_group):
                    dpg.add_checkbox(label='Pointer',
                                     tag=f'selected_declaration[{i}]_is_pointer',
                                     indent=50,
                                     default_value=declaration['is_pointer'],
                                     user_data=i,
                                     callback=lambda s, data: (
                                         self.gui.selected_node.declarations[dpg.get_item_user_data(s)]
                                         .update({'is_pointer': data}),
                                         self.gui.on_select_node(self.gui.selected_node),
                                         self.gui.redraw_all()))

                with dpg.group(horizontal=True, parent=self.main_group):
                    dpg.add_checkbox(label='Array',
                                     tag=f'selected_declaration[{i}]_is_array',
                                     indent=50,
                                     default_value=declaration['is_array'],
                                     user_data=i,
                                     callback=lambda s, data: (
                                         self.gui.selected_node.declarations[dpg.get_item_user_data(s)]
                                         .update({'is_array': data}),
                                         self.gui.on_select_node(self.gui.selected_node),
                                         self.gui.redraw_all()))

                with dpg.group(horizontal=True, tag=f'selected_declaration[{i}]_array_size_group',
                               parent=self.main_group, show=declaration['is_array']):
                    dpg.add_text('Size')
                    dpg.add_input_text(tag=f'selected_declaration[{i}]_array_size',
                                       indent=50,
                                       width=-1,
                                       no_spaces=True,
                                       default_value=declaration['array_size'],
                                       user_data=i,
                                       callback=lambda s, data: (
                                           self.gui.selected_node.declarations[dpg.get_item_user_data(s)]
                                           .update({'array_size': data}),
                                           self.gui.redraw_all()))

                with dpg.group(horizontal=True, parent=self.main_group):
                    dpg.add_checkbox(label='Static',
                                     tag=f'selected_declaration[{i}]_is_static',
                                     indent=50,
                                     default_value=declaration['is_static'],
                                     user_data=i,
                                     callback=lambda s, data: (
                                         self.gui.selected_node.declarations[dpg.get_item_user_data(s)]
                                         .update({'is_static': data}),
                                         self.gui.on_select_node(self.gui.selected_node),
                                         self.gui.redraw_all()))
                with dpg.group(horizontal=True, tag=f'selected_declaration[{i}]_var_value_group',
                               show=not declaration['is_array'], parent=self.main_group):
                    dpg.add_text('Value')
                    dpg.add_input_text(tag=f'selected_declaration[{i}]_var_value',
                                       indent=50,
                                       width=-1,
                                       default_value=declaration['var_value'],
                                       user_data=i,
                                       callback=lambda s, data: (
                                           self.gui.selected_node.declarations[dpg.get_item_user_data(s)]
                                           .update({'var_value': data}),
                                           self.gui.redraw_all()))

                dpg.add_spacer(height=5, parent=self.main_group)
                dpg.add_separator(parent=self.main_group)
            dpg.add_spacer(height=5, parent=self.main_group)
            dpg.add_button(label='Add Declaration', width=-1,
                           parent=self.main_group, callback=self.on_add_declaration)

    def on_add_declaration(self) -> None:
        if isinstance(self.gui.selected_node, Declarations):
            self.gui.selected_node.add_declaration()
        self.refresh()
        self.gui.redraw_all()

    def on_delete_declaration(self, index: int) -> None:
        if isinstance(self.gui.selected_node, Declarations):
            self.gui.selected_node.delete_declaration(index)
        self.refresh()
        self.gui.redraw_all()

    def hide(self) -> None:
        dpg.hide_item(self.main_group)

    def show(self, node: Optional[Node]) -> None:
        if not isinstance(node, Declarations):
            return
        self.gui.set_sidebar_title('Declaration')
        self.refresh()
        dpg.show_item(self.main_group)
