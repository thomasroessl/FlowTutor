from __future__ import annotations
from typing import TYPE_CHECKING
import dearpygui.dearpygui as dpg

from flowtutor.flowchart.parameter import Parameter
from flowtutor.language import Language

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SidebarFunctionStart:

    def __init__(self, gui: GUI) -> None:
        self.gui = gui
        with dpg.group(tag='selected_function_start', show=False):
            header = dpg.add_text('Function')
            dpg.bind_item_font(header, 'header_font')

            with dpg.group(tag='selected_function_parameters_group', show=False):
                dpg.add_separator()
                dpg.add_text('Parameters')
                with dpg.table(header_row=True, sortable=False, hideable=False, reorderable=False,
                               borders_innerH=True, borders_outerH=True, borders_innerV=True,
                               borders_outerV=True) as parameter_table:

                    self.table = parameter_table

                    dpg.add_table_column(label='Name')
                    dpg.add_table_column(label='Type')
                    dpg.add_table_column(label='', width_fixed=True, width=10)

                    self.refresh_entries([])

                    with dpg.theme() as item_theme:
                        with dpg.theme_component(dpg.mvTable):
                            dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 0, 1, category=dpg.mvThemeCat_Core)
                    dpg.bind_item_theme(parameter_table, item_theme)

                dpg.add_button(label='Add Parameter',
                               callback=lambda: (gui.selected_node.__getattribute__('parameters')
                                                 .append(Parameter()),
                                                 self.refresh_entries(
                                   gui.selected_node.__getattribute__('parameters')),
                                   gui.redraw_all()))

                dpg.add_spacer(height=5)
                dpg.add_separator()

            with dpg.group(tag='selected_function_return_type_group'):
                dpg.add_text('Return Type')
                dpg.add_combo(Language.get_data_types(),
                              tag='selected_function_return_type',
                              width=-1,
                              callback=lambda _, data: (gui.selected_node.__setattr__('return_type', data),
                                                        gui.redraw_all()))

    def refresh_entries(self, entries):
        # delete existing rows in the table to avoid duplicates
        for child in dpg.get_item_children(self.table)[1]:
            dpg.delete_item(child)

        for i, entry in enumerate(entries):
            with dpg.table_row(parent=self.table):
                dpg.add_input_text(width=-1, height=-1,
                                   callback=lambda _, data: (self.gui.selected_node.__getattribute__('parameters')[i]
                                                             .__setattr__('name', data),
                                                             self.gui.redraw_all()),
                                   no_spaces=True, default_value=entry.name)
                dpg.add_combo(Language.get_data_types(),
                              callback=lambda _, data: (self.gui.selected_node.__getattribute__('parameters')[i]
                                                        .__setattr__('type', data),
                                                        self.gui.redraw_all()),
                              width=-1, default_value=entry.type)
                dpg.add_button(label='X', callback=lambda: (
                    self.gui.selected_node.__getattribute__('parameters').pop(i),
                    self.refresh_entries(self.gui.selected_node.__getattribute__('parameters'))
                ))
