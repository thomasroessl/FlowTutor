from __future__ import annotations
from typing import TYPE_CHECKING, List
import dearpygui.dearpygui as dpg
from flowtutor.flowchart.struct_definition import StructDefinition
from flowtutor.flowchart.struct_member import StructMember
from flowtutor.language import Language

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


HEADER_TAG = 'struct_header'


class SectionStructs:
    def __init__(self, gui: GUI) -> None:
        self.gui = gui
        with dpg.theme() as self.delete_button_theme:
            with dpg.theme_component(dpg.mvImageButton):
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 3, 3, category=dpg.mvThemeCat_Core)
        dpg.add_collapsing_header(label='Structures', tag=HEADER_TAG)
        self.refresh()

    def refresh(self):
        for child in dpg.get_item_children(HEADER_TAG)[1]:
            dpg.delete_item(child)
        for [i, d] in enumerate(self.struct_definitions()):
            if i > 0:
                dpg.add_spacer(height=5, parent=HEADER_TAG)
            with dpg.group(horizontal=True, parent=HEADER_TAG):
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
            with dpg.group(parent=HEADER_TAG):
                with dpg.table(header_row=True, sortable=False, hideable=False, reorderable=False,
                               borders_innerH=True, borders_outerH=True, borders_innerV=True,
                               borders_outerV=True) as table:

                    dpg.add_table_column(label='Member Name')
                    dpg.add_table_column(label='Type')
                    dpg.add_table_column(label='Ptr', width_fixed=True, width=11)
                    dpg.add_table_column(label='Arr', width_fixed=True, width=11)
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

            dpg.add_spacer(height=5, parent=HEADER_TAG)
            dpg.add_separator(parent=HEADER_TAG)
        dpg.add_spacer(height=5, parent=HEADER_TAG)
        dpg.add_button(label='Add Structure', parent=HEADER_TAG, width=-1, callback=self.on_add_definition)

    def on_add_definition(self):
        self.struct_definitions().append(StructDefinition())
        self.refresh()
        self.gui.redraw_all()

    def on_delete_definition(self, index: int):
        del self.struct_definitions()[index]
        self.refresh()
        self.gui.redraw_all()

    def main_node(self):
        return self.gui.flowcharts['main']

    def struct_definitions(self):
        return self.main_node().struct_definitions

    def members(self, i):
        return self.struct_definitions()[i].__getattribute__('members')

    def member(self, t: tuple[int, int]):
        i, j = t
        return self.members(i)[j]

    def refresh_members(self, i, table, members: List[StructMember]):
        # delete existing rows in the table to avoid duplicates
        for child in dpg.get_item_children(table)[1]:
            dpg.delete_item(child)

        for j, member in enumerate(members):
            with dpg.table_row(parent=table):
                dpg.add_input_text(width=-1,
                                   height=-1,
                                   user_data=(i, j),
                                   callback=lambda s, data: (self.member(dpg.get_item_user_data(s))
                                                             .__setattr__('name', data),
                                                             self.gui.redraw_all()),
                                   no_spaces=True, default_value=member.name)

                dpg.add_combo(Language.get_data_types(),
                              user_data=(i, j),
                              callback=lambda s, data: (self.member(dpg.get_item_user_data(s))
                                                        .__setattr__('type', data),
                                                        self.gui.redraw_all()),
                              width=-1,
                              default_value=member.type)

                dpg.add_checkbox(user_data=(i, j),
                                 callback=lambda s, data: (self.member(dpg.get_item_user_data(s))
                                                           .__setattr__('is_pointer', data),
                                                           self.gui.redraw_all()),
                                 default_value=member.is_pointer)

                dpg.add_checkbox(user_data=(i, j),
                                 callback=lambda s, data: (self.member(dpg.get_item_user_data(s))
                                                           .__setattr__('is_array', data),
                                                           self.gui.redraw_all()),
                                 default_value=member.is_array)

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