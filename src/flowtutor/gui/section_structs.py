from __future__ import annotations
from typing import TYPE_CHECKING, Union
import dearpygui.dearpygui as dpg
from flowtutor.flowchart.flowchart import Flowchart
from flowtutor.flowchart.struct_definition import StructDefinition
from flowtutor.flowchart.struct_member import StructMember
from flowtutor.language import Language

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SectionStructs:
    def __init__(self, gui: GUI) -> None:
        self.gui = gui
        with dpg.theme() as self.delete_button_theme:
            with dpg.theme_component(dpg.mvImageButton):
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 3, 3, category=dpg.mvThemeCat_Core)
        self.main_header = dpg.add_collapsing_header(label='Structures')
        self.refresh()

    def refresh(self) -> None:
        for child in dpg.get_item_children(self.main_header)[1]:
            dpg.delete_item(child)
        for [i, d] in enumerate(self.struct_definitions()):
            if i > 0:
                dpg.add_spacer(height=5, parent=self.main_header)
            with dpg.group(horizontal=True, parent=self.main_header):
                dpg.add_text('Name')
                dpg.add_input_text(indent=50,
                                   width=-33,
                                   no_spaces=True,
                                   default_value=d.name,
                                   user_data=i,
                                   callback=lambda s, data: (
                                       self.struct_definitions()[dpg.get_item_user_data(
                                           s)].__setattr__('name', data),
                                       self.gui.redraw_all()))
                delete_button = dpg.add_image_button(
                    'trash_image', height=18, width=18, user_data=i,
                    callback=lambda s: self.on_delete_definition(dpg.get_item_user_data(s)))
                dpg.bind_item_theme(delete_button, self.delete_button_theme)
            with dpg.group(parent=self.main_header):
                with dpg.table(header_row=True, sortable=False, hideable=False, reorderable=False,
                               borders_innerH=True, borders_outerH=True, borders_innerV=True,
                               borders_outerV=True) as table:

                    dpg.add_table_column(label='Member Name')
                    dpg.add_table_column(label='Type')
                    dpg.add_table_column(label='Ptr', width_fixed=True, width=11)
                    dpg.add_table_column(label='Arr', width_fixed=True, width=11)
                    dpg.add_table_column(label='Size')
                    dpg.add_table_column(label='', width_fixed=True, width=12)

                    self.refresh_members(i, table, d.members)

                    with dpg.theme() as item_theme:
                        with dpg.theme_component(dpg.mvTable):
                            dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 0, 1, category=dpg.mvThemeCat_Core)
                    dpg.bind_item_theme(table, item_theme)

                dpg.add_button(label='Add Member',
                               user_data=(i, table),
                               callback=lambda s: (self.members(dpg.get_item_user_data(s)[0]).append(StructMember()),
                                                   self.refresh_members(dpg.get_item_user_data(s)[0],
                                                                        dpg.get_item_user_data(s)[1],
                                                                        self.members(dpg.get_item_user_data(s)[0]))))

            dpg.add_spacer(height=5, parent=self.main_header)
            dpg.add_separator(parent=self.main_header)
        dpg.add_spacer(height=5, parent=self.main_header)
        dpg.add_button(label='Add Structure', parent=self.main_header, width=-1, callback=self.on_add_definition)

    def on_add_definition(self) -> None:
        self.struct_definitions().append(StructDefinition())
        self.refresh()
        self.gui.redraw_all()

    def on_delete_definition(self, index: int) -> None:
        del self.struct_definitions()[index]
        self.refresh()
        self.gui.redraw_all()

    def main_node(self) -> Flowchart:
        return self.gui.flowcharts['main']

    def struct_definitions(self) -> list[StructDefinition]:
        return self.main_node().struct_definitions

    def members(self, i: int) -> list[StructMember]:
        result: list[StructMember] = self.struct_definitions()[i].__getattribute__('members')
        return result

    def member(self, t: tuple[int, int]) -> StructMember:
        i, j = t
        return self.members(i)[j]

    def toggle_is_array(self, is_array: bool, checkbox_id: Union[int, str]) -> None:
        i, j = dpg.get_item_user_data(checkbox_id)
        member = self.member((i, j))
        if is_array:
            dpg.show_item(f'struct_member_array_size_{i}_{j}')
        else:
            dpg.hide_item(f'struct_member_array_size_{i}_{j}')

        dpg.configure_item(f'struct_member_is_pointer_{i}_{j}', default_value=member.is_pointer)

    def toggle_is_pointer(self, checkbox_id: Union[int, str]) -> None:
        i, j = dpg.get_item_user_data(checkbox_id)
        member = self.member((i, j))
        dpg.configure_item(f'struct_member_array_size_{i}_{j}', default_value=member.array_size)
        dpg.configure_item(f'struct_member_is_array_{i}_{j}', default_value=member.is_array)

    def refresh_members(self, i: int, table: Union[int, str], members: list[StructMember]) -> None:
        # delete existing rows in the table to avoid duplicates
        for child in dpg.get_item_children(table)[1]:
            dpg.delete_item(child)

        for j, member in enumerate(members):
            with dpg.table_row(parent=table):
                dpg.add_input_text(width=-1,
                                   user_data=(i, j),
                                   callback=lambda s, data: (self.member(dpg.get_item_user_data(s))
                                                             .__setattr__('name', data),
                                                             self.gui.redraw_all()),
                                   no_spaces=True, default_value=member.name)

                dpg.add_combo(Language.get_data_types(self.gui.flowcharts['main']),
                              width=-1,
                              user_data=(i, j),
                              callback=lambda s, data: (self.member(dpg.get_item_user_data(s))
                                                        .__setattr__('type', data),
                                                        self.gui.redraw_all()),
                              default_value=member.type)

                dpg.add_checkbox(user_data=(i, j),
                                 tag=f'struct_member_is_pointer_{i}_{j}',
                                 callback=lambda s, data: (self.member(dpg.get_item_user_data(s))
                                                           .__setattr__('is_pointer', data),
                                                           self.toggle_is_pointer(s),
                                                           self.gui.redraw_all()),
                                 default_value=member.is_pointer)

                dpg.add_checkbox(user_data=(i, j),
                                 tag=f'struct_member_is_array_{i}_{j}',
                                 callback=lambda s, data: (self.member(dpg.get_item_user_data(s))
                                                           .__setattr__('is_array', data),
                                                           self.toggle_is_array(data, s),
                                                           self.gui.redraw_all()),
                                 default_value=member.is_array)

                dpg.add_input_text(user_data=(i, j),
                                   tag=f'struct_member_array_size_{i}_{j}',
                                   width=-1,
                                   callback=lambda s, data: (self.member(dpg.get_item_user_data(s))
                                                             .__setattr__('array_size', data),
                                                             self.gui.redraw_all()),
                                   default_value=member.array_size,
                                   show=member.is_array)

                delete_button = dpg.add_image_button(
                    'trash_image',
                    user_data=(i, j),
                    callback=lambda s: (
                        self.members(dpg.get_item_user_data(s)[0]).pop(dpg.get_item_user_data(s)[1]),
                        self.refresh_members(
                            dpg.get_item_user_data(s)[0],
                            table,
                            self.members(dpg.get_item_user_data(s)[0])),
                        self.gui.redraw_all()))

                with dpg.theme() as delete_button_theme:
                    with dpg.theme_component(dpg.mvImageButton):
                        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 5, 4, category=dpg.mvThemeCat_Core)

                dpg.bind_item_theme(delete_button, delete_button_theme)
