from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import dearpygui.dearpygui as dpg
from flowtutor.flowchart.declaration import Declaration
from flowtutor.flowchart.node import Node
from flowtutor.gui.sidebar import Sidebar
from flowtutor.language import Language

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SidebarDeclaration(Sidebar):

    def __init__(self, gui: GUI) -> None:
        self.gui = gui
        with dpg.group(show=False) as self.main_group:
            with dpg.group(horizontal=True):
                dpg.add_text('Name')
                dpg.add_input_text(tag='selected_declaration_name',
                                   indent=50,
                                   width=-1,
                                   no_spaces=True,
                                   callback=lambda _, data: (gui.selected_node.__setattr__(
                                       'var_name', data),
                                       gui.redraw_all()))
            with dpg.group(horizontal=True):
                dpg.add_text('Type')
                dpg.add_combo(Language.get_data_types(gui.flowcharts['main']),
                              tag='selected_declaration_type',
                              indent=50,
                              width=-1,
                              callback=lambda _, data: (gui.selected_node.__setattr__('var_type', data),
                                                        gui.redraw_all()))

            with dpg.group(horizontal=True):
                dpg.add_checkbox(label='Pointer',
                                 tag='selected_declaration_is_pointer',
                                 indent=50,
                                 callback=lambda _, data: (gui.selected_node.__setattr__('is_pointer',
                                                                                         data),
                                                           gui.on_select_node(gui.selected_node),
                                                           gui.redraw_all()))

            with dpg.group(horizontal=True):
                dpg.add_checkbox(label='Array',
                                 tag='selected_declaration_is_array',
                                 indent=50,
                                 callback=lambda _, data: (gui.selected_node.__setattr__('is_array',
                                                                                         data),
                                                           gui.on_select_node(gui.selected_node),
                                                           gui.redraw_all()))

            with dpg.group(horizontal=True, tag='selected_declaration_array_size_group', show=False):
                dpg.add_text('Size')
                dpg.add_input_text(tag='selected_declaration_array_size',
                                   indent=50,
                                   width=-1,
                                   no_spaces=True,
                                   callback=lambda _, data: (gui.selected_node.__setattr__(
                                       'array_size', data),
                                       gui.redraw_all()))
            with dpg.group(horizontal=True):
                dpg.add_checkbox(label='Static',
                                 tag='selected_declaration_is_static',
                                 indent=50,
                                 callback=lambda _, data: (gui.selected_node.__setattr__('is_static',
                                                                                         data),
                                                           gui.on_select_node(gui.selected_node),
                                                           gui.redraw_all()))
            with dpg.group(horizontal=True, tag='selected_declaration_var_value_group'):
                dpg.add_text('Value')
                dpg.add_input_text(tag='selected_declaration_var_value',
                                   indent=50,
                                   width=-1,
                                   callback=lambda _, data: (gui.selected_node.__setattr__(
                                       'var_value', data),
                                       gui.redraw_all()))

    def hide(self) -> None:
        dpg.hide_item(self.main_group)

    def show(self, node: Optional[Node]) -> None:
        if not isinstance(node, Declaration):
            return
        self.gui.set_sidebar_title('Declaration')
        dpg.configure_item('selected_declaration_name', default_value=node.var_name)
        dpg.configure_item('selected_declaration_type', default_value=node.var_type)
        dpg.configure_item('selected_declaration_var_value', default_value=node.var_value)
        dpg.configure_item('selected_declaration_is_array', default_value=node.is_array)
        if node.is_array:
            dpg.show_item('selected_declaration_array_size_group')
            dpg.hide_item('selected_declaration_var_value_group')
        else:
            dpg.hide_item('selected_declaration_array_size_group')
            dpg.show_item('selected_declaration_var_value_group')
        dpg.configure_item('selected_declaration_array_size', default_value=node.array_size)
        dpg.configure_item('selected_declaration_is_pointer', default_value=node.is_pointer)
        dpg.show_item(self.main_group)
