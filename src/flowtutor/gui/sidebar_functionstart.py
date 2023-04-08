from __future__ import annotations
from typing import TYPE_CHECKING
import dearpygui.dearpygui as dpg
from dependency_injector.wiring import Provide, inject

from flowtutor.flowchart.functionstart import FunctionStart
from flowtutor.flowchart.parameter import Parameter
from flowtutor.language import Language
from flowtutor.modal_service import ModalService

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SidebarFunctionStart:

    @inject
    def __init__(self, gui: GUI, modal_service: ModalService = Provide['modal_service']) -> None:
        self.gui = gui
        self.modal_service = modal_service
        with dpg.group(tag='selected_function_start', show=False):
            header = dpg.add_text('Function')

            with dpg.group(tag='selected_function_start_management', horizontal=True, show=False):
                dpg.add_button(label='Rename', callback=self.on_rename)
                dpg.add_button(label='Delete', callback=self.on_delete)

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

    def on_delete(self):
        if isinstance(self.gui.selected_node, FunctionStart):
            del self.gui.flowcharts[self.gui.selected_node.name]
            self.gui.refresh_function_tabs()

    def on_rename(self):
        if isinstance(self.gui.selected_node, FunctionStart):
            self.modal_service.show_input_text_modal(
                'Rename', 'Function Name', self.gui.selected_node.name, self.rename)

    def rename(self, name):
        if isinstance(self.gui.selected_node, FunctionStart):
            fun = self.gui.flowcharts[self.gui.selected_node.name]
            del self.gui.flowcharts[self.gui.selected_node.name]
            self.gui.selected_node.name = name
            self.gui.flowcharts[name] = fun
            self.gui.refresh_function_tabs()

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

        # Hide function management buttons for main (cannot be renamed or deleted)
        if isinstance(self.gui.selected_node, FunctionStart):
            if self.gui.selected_node.name == 'main':
                dpg.hide_item('selected_function_start_management')
            else:
                dpg.show_item('selected_function_start_management')
