from __future__ import annotations
from typing import TYPE_CHECKING
import dearpygui.dearpygui as dpg
from flowtutor.language import Language

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SidebarDeclaration:
    def __init__(self, gui: GUI) -> None:
        with dpg.group(tag='selected_declaration', show=False):
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
                dpg.add_combo(Language.get_data_types(),
                              tag='selected_declaration_type',
                              indent=50,
                              width=-1,
                              callback=lambda _, data: (gui.selected_node.__setattr__('var_type', data),
                                                        gui.redraw_all()))
            if Language.has_pointers():
                with dpg.group(horizontal=True):
                    dpg.add_checkbox(label='Pointer',
                                     tag='selected_declaration_is_pointer',
                                     indent=50,
                                     callback=lambda _, data: (gui.selected_node.__setattr__('is_pointer',
                                                                                             data),
                                                               gui.on_select_node(gui.selected_node),
                                                               gui.redraw_all()))
            if Language.has_arrays():
                with dpg.group(horizontal=True):
                    dpg.add_checkbox(label='Array',
                                     tag='selected_declaration_is_array',
                                     indent=50,
                                     callback=lambda _, data: (gui.selected_node.__setattr__('is_array',
                                                                                             data),
                                                               gui.on_select_node(gui.selected_node),
                                                               gui.redraw_all()))
            if Language.has_arrays():
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
