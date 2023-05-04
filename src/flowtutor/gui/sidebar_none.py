from __future__ import annotations
from typing import TYPE_CHECKING
import dearpygui.dearpygui as dpg

from flowtutor.language import Language

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class SidebarNone:

    def __init__(self, gui: GUI) -> None:
        self.gui = gui
        with dpg.group(tag='selected_none'):
            with dpg.collapsing_header(label='Include'):
                for header in Language.get_standard_headers():
                    dpg.add_checkbox(
                        label=header, default_value=header in self.gui.flowcharts['main']
                        .__getattribute__('includes'),
                        user_data=header,
                        callback=self.on_header_checkbox_change)
            with dpg.collapsing_header(label='Define'):
                with dpg.table(sortable=False, hideable=False, reorderable=False,
                               borders_innerH=True, borders_outerH=True, borders_innerV=True,
                               borders_outerV=True) as self.table:

                    dpg.add_table_column()
                    dpg.add_table_column(width_fixed=True, width=12)

                    self.refresh_definitions([])
                    with dpg.theme() as item_theme:
                        with dpg.theme_component(dpg.mvTable):
                            dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 0, 1, category=dpg.mvThemeCat_Core)
                    dpg.bind_item_theme(self.table, item_theme)

                dpg.add_button(label='Add Definition',
                               callback=lambda: (self.gui.flowcharts['main']
                                                 .__getattribute__('preprocessor_definitions').append(''),
                                                 self.refresh_definitions(
                                   self.gui.flowcharts['main'].__getattribute__('preprocessor_definitions')),
                                   gui.redraw_all()))
            with dpg.collapsing_header(label='Custom'):
                dpg.add_input_text(tag='selected_preprocessor_custom',
                                   width=-1,
                                   height=-1,
                                   multiline=True,
                                   callback=lambda _, data:
                                   (self.gui.flowcharts['main']  # type: ignore [func-returns-value]
                                    .__setattr__('preprocessor_custom', data),
                                    gui.redraw_all()))

    def on_header_checkbox_change(self, sender, is_checked):
        header = dpg.get_item_user_data(sender)
        if is_checked:
            self.gui.flowcharts['main'].__getattribute__('includes').append(header)
        else:
            self.gui.flowcharts['main'].__getattribute__('includes').remove(header)
        self.gui.redraw_all()

    def refresh_definitions(self, entries):
        # delete existing rows in the table to avoid duplicates
        for child in dpg.get_item_children(self.table)[1]:
            dpg.delete_item(child)

        for i, entry in enumerate(entries):
            with dpg.table_row(parent=self.table):
                dpg.add_input_text(width=-1, height=-1, user_data=i,
                                   callback=lambda s, data: (self.gui.flowcharts['main']
                                                             .__getattribute__('preprocessor_definitions')
                                                             .__setitem__(dpg.get_item_user_data(s), data),
                                                             self.gui.redraw_all()),
                                   no_spaces=True, default_value=entry)

                delete_button = dpg.add_image_button('trash_image', user_data=i, callback=lambda s: (
                    self.gui.flowcharts['main'].__getattribute__(
                        'preprocessor_definitions').pop(dpg.get_item_user_data(s)),
                    self.refresh_definitions(self.gui.flowcharts['main'].__getattribute__('preprocessor_definitions')),
                    self.gui.redraw_all()
                ))
                with dpg.theme() as delete_button_theme:
                    with dpg.theme_component(dpg.mvImageButton):
                        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 5, 4, category=dpg.mvThemeCat_Core)

                dpg.bind_item_theme(delete_button, delete_button_theme)
