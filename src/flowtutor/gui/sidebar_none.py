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

    def on_header_checkbox_change(self, sender, is_checked):
        header = dpg.get_item_user_data(sender)
        if is_checked:
            self.gui.flowcharts['main'].__getattribute__('includes').append(header)
        else:
            self.gui.flowcharts['main'].__getattribute__('includes').remove(header)
        self.gui.redraw_all()
