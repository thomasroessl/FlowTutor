from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import dearpygui.dearpygui as dpg
from dependency_injector.wiring import Provide, inject

from flowtutor.flowchart.template import Template
from flowtutor.gui.sidebar import Sidebar

if TYPE_CHECKING:
    from flowtutor.gui.gui import GUI
    from flowtutor.flowchart.node import Node
    from flowtutor.language_service import LanguageService


class SidebarTemplate(Sidebar):
    '''A GUI sidebar for template nodes.'''

    @inject
    def __init__(self, gui: GUI, language_service: LanguageService = Provide['language_service']) -> None:
        self.gui = gui
        self.language_service = language_service
        self.main_group = dpg.add_group(show=False)

    def hide(self) -> None:
        for child in dpg.get_item_children(self.main_group)[1]:
            dpg.delete_item(child)
        dpg.hide_item(self.main_group)

    def show(self, node: Optional[Node]) -> None:
        if not isinstance(node, Template):
            return
        self.gui.set_sidebar_title(node.data['label'])
        dpg.show_item(self.main_group)
        with dpg.group(parent=self.main_group):
            for parameter in node.parameters:
                if 'visible' in parameter and not eval(f"{parameter['visible']}", node.values):
                    continue
                var_type = parameter['type'] if 'type' in parameter else 'text'

                if var_type == 'checkbox':
                    with dpg.group(horizontal=True):
                        dpg.add_checkbox(label=parameter['label'],
                                         default_value=node.values.__getitem__(parameter['name']) or False,
                                         user_data=parameter,
                                         callback=lambda s, data:
                                         (node.values.__setitem__(dpg.get_item_user_data(s)['name'], data),
                                          self.gui.redraw_all(True),
                                          self.hide(),
                                          self.show(node)))
                elif var_type == 'textarea':
                    with dpg.group():
                        dpg.add_text(parameter['label'])
                        dpg.add_input_text(width=-1,
                                           height=-200,
                                           multiline=True,
                                           default_value=node.values.__getitem__(parameter['name']) or '',
                                           user_data=parameter,
                                           callback=lambda s, data:
                                           (node.values.__setitem__(dpg.get_item_user_data(s)['name'], data),
                                            self.gui.redraw_all(True)))
                else:  # var_type == 'text'
                    with dpg.group():
                        dpg.add_text(parameter['label'])
                        if 'options' in parameter:
                            options = parameter['options']
                            if options == '{{TYPES}}':
                                options = self.language_service.get_data_types(self.gui.selected_flowchart)
                            dpg.add_combo(options,
                                          width=-1,
                                          default_value=node.values.__getitem__(parameter['name']) or '',
                                          user_data=parameter,
                                          callback=lambda s, data:
                                          (node.values.__setitem__(dpg.get_item_user_data(s)['name'], data),
                                           self.gui.redraw_all(True)))
                        else:
                            dpg.add_input_text(width=-1,
                                               default_value=node.values.__getitem__(parameter['name']) or '',
                                               user_data=parameter,
                                               callback=lambda s, data:
                                               (node.values.__setitem__(dpg.get_item_user_data(s)['name'], data),
                                                self.gui.redraw_all(True)))
        dpg.split_frame()
