from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import dearpygui.dearpygui as dpg
from dependency_injector.wiring import Provide, inject

from flowtutor.flowchart.functionstart import FunctionStart
from flowtutor.flowchart.node import Node
from flowtutor.flowchart.parameter import Parameter
from flowtutor.gui.sidebar import Sidebar
from flowtutor.language import Language
from flowtutor.modal_service import ModalService

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SidebarFunctionStart(Sidebar):

    @inject
    def __init__(self, gui: GUI, modal_service: ModalService = Provide['modal_service']) -> None:
        self.gui = gui
        self.modal_service = modal_service
        with dpg.group(show=False) as self.main_group:
            dpg.configure_item(gui.rename_button, callback=self.on_rename)
            dpg.configure_item(gui.delete_button, callback=self.on_delete)

            with dpg.group(tag='selected_function_parameters_group', show=False):
                dpg.add_text('Parameters')
                with dpg.table(header_row=True, sortable=False, hideable=False, reorderable=False,
                               borders_innerH=True, borders_outerH=True, borders_innerV=True,
                               borders_outerV=True) as self.table:

                    dpg.add_table_column(label='Name')
                    dpg.add_table_column(label='Type')
                    dpg.add_table_column(label='', width_fixed=True, width=12)

                    self.refresh_entries([])

                    with dpg.theme() as item_theme:
                        with dpg.theme_component(dpg.mvTable):
                            dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 0, 1, category=dpg.mvThemeCat_Core)
                    dpg.bind_item_theme(self.table, item_theme)

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
                dpg.add_combo(Language.get_data_types(self.gui.flowcharts['main']),
                              tag='selected_function_return_type',
                              width=-1,
                              callback=lambda _, data: (gui.selected_node.__setattr__('return_type', data),
                                                        gui.redraw_all()))

    def parameters(self) -> list[Parameter]:
        result: list[Parameter] = self.gui.selected_node.__getattribute__('parameters')
        return result

    def on_delete(self) -> None:
        if isinstance(self.gui.selected_node, FunctionStart):
            del self.gui.flowcharts[self.gui.selected_node.name]
            self.gui.refresh_function_tabs()

    def on_rename(self) -> None:
        if isinstance(self.gui.selected_node, FunctionStart):
            self.modal_service.show_input_text_modal(
                'Rename', 'Function Name', self.gui.selected_node.name, self.rename)

    def rename(self, name: str) -> None:
        if isinstance(self.gui.selected_node, FunctionStart):
            fun = self.gui.flowcharts[self.gui.selected_node.name]
            del self.gui.flowcharts[self.gui.selected_node.name]
            self.gui.selected_node.name = name
            self.gui.flowcharts[name] = fun
            self.gui.refresh_function_tabs()

    def refresh_entries(self, entries: list[Parameter]) -> None:
        # delete existing rows in the table to avoid duplicates
        for child in dpg.get_item_children(self.table)[1]:
            dpg.delete_item(child)

        for i, entry in enumerate(entries):
            with dpg.table_row(parent=self.table):
                dpg.add_input_text(width=-1,
                                   height=-1,
                                   user_data=i,
                                   callback=lambda s, data: (self.parameters()[dpg.get_item_user_data(s)]
                                                             .__setattr__('name', data),
                                                             self.gui.redraw_all()),
                                   no_spaces=True, default_value=entry.name)
                dpg.add_combo(Language.get_data_types(self.gui.flowcharts['main']),
                              user_data=i,
                              callback=lambda s, data: (self.parameters()[dpg.get_item_user_data(s)]
                                                        .__setattr__('type', data),
                                                        self.gui.redraw_all()),
                              width=-1, default_value=entry.type)

                delete_button = dpg.add_image_button('trash_image', user_data=i, callback=lambda s: (
                    self.parameters().pop(dpg.get_item_user_data(s)),
                    self.refresh_entries(self.parameters()),
                    self.gui.redraw_all()
                ))
                with dpg.theme() as delete_button_theme:
                    with dpg.theme_component(dpg.mvImageButton):
                        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 5, 4, category=dpg.mvThemeCat_Core)

                dpg.bind_item_theme(delete_button, delete_button_theme)

        # Hide function management buttons for main (cannot be renamed or deleted)
        if isinstance(self.gui.selected_node, FunctionStart):
            if self.gui.selected_node.name == 'main':
                dpg.hide_item('function_management_group')
            else:
                dpg.show_item('function_management_group')

    def hide(self) -> None:
        dpg.hide_item(self.main_group)

    def show(self, node: Optional[Node]) -> None:
        if not isinstance(node, FunctionStart):
            return
        self.gui.set_sidebar_title('Function')
        dpg.configure_item('selected_function_return_type', default_value=node.return_type)
        self.refresh_entries(node.__getattribute__('parameters'))
        dpg.show_item(self.main_group)
        # hide return type selection for 'main', because it has to always return int
        if node.name == 'main':
            dpg.hide_item('selected_function_return_type_group')
            dpg.hide_item('selected_function_parameters_group')
            dpg.hide_item(self.gui.section_node_extras.node_is_comment_group)
        else:
            dpg.show_item('selected_function_return_type_group')
            dpg.show_item('selected_function_parameters_group')
