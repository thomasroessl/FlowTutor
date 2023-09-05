from __future__ import annotations
import platform
from typing import TYPE_CHECKING
import dearpygui.dearpygui as dpg
from dependency_injector.wiring import Provide, inject

from flowtutor.containers import Container
from flowtutor.gui.gui import GUI

if TYPE_CHECKING:
    from flowtutor.util_service import UtilService


@inject
def start(utils_service: UtilService = Provide['utils_service']) -> None:
    if platform.system() != 'Windows':
        utils_service.open_tty()
    gui = GUI(2000, 2000)
    # Calls the redraw function after the first frame is rendered
    if dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()
        gui.redraw_all(True)
    dpg.start_dearpygui()
    if platform.system() != 'Windows':
        utils_service.stop_tty()
    dpg.destroy_context()
    utils_service.cleanup_temp()


def main() -> None:
    container = Container()
    container.init_resources()
    container.wire(modules=[__name__,
                            'flowtutor.codegenerator',
                            'flowtutor.debugsession',
                            'flowtutor.gui.debugger',
                            'flowtutor.gui.gui',
                            'flowtutor.gui.sidebar_none',
                            'flowtutor.gui.sidebar_functionstart',
                            'flowtutor.gui.sidebar_template',
                            'flowtutor.gui.section_structs',
                            'flowtutor.modal_service',
                            'flowtutor.language_service',
                            'flowtutor.flowchart.template',
                            'flowtutor.flowchart.functionstart',
                            'flowtutor.flowchart.functionend'])
    start()


if __name__ == '__main__':
    main()
