from __future__ import annotations
from typing import TYPE_CHECKING
import dearpygui.dearpygui as dpg

from flowtutor.gui.section_structs import SectionStructs
from flowtutor.gui.section_typedefs import SectionTypedefs

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI


class WindowTypes:
    '''A GUI windo for type and struct definitions.'''

    def __init__(self, gui: GUI) -> None:
        with dpg.window(tag='type_window',
                        label='Types',
                        pos=(300, 75),
                        width=600,
                        height=500,
                        no_collapse=True,
                        show=False):
            self.section_typedefs = SectionTypedefs(gui)
            self.section_structs = SectionStructs(gui)

    def refresh(self) -> None:
        self.section_typedefs.refresh()
        self.section_structs.refresh()
