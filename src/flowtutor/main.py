import dearpygui.dearpygui as dpg
from dependency_injector.wiring import Provide, inject

from flowtutor.containers import Container
from flowtutor.gui.gui import GUI
from flowtutor.util_service import UtilService


@inject
def start(utils_service: UtilService = Provide['utils_service']):
    gui = GUI(2000, 2000)
    # Calls the redraw function after the first frame is rendered
    if dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()
        gui.redraw_all()
    dpg.start_dearpygui()
    dpg.destroy_context()
    utils_service.cleanup_temp()


def main():
    container = Container()
    container.init_resources()
    container.wire(modules=[__name__,
                            'flowtutor.codegenerator',
                            'flowtutor.debugsession',
                            'flowtutor.debugger',
                            'flowtutor.gui.gui'])
    start()


if __name__ == '__main__':
    main()
