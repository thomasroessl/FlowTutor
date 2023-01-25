import dearpygui.dearpygui as dpg

from flowtutor.gui import GUI
from flowtutor.utils import Utils


def main():
    gui = GUI(2000, 2000)
    utils = Utils()
    # Calls the redraw function after the first frame is rendered
    if dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()
        gui.redraw_all()
    dpg.start_dearpygui()
    dpg.destroy_context()
    utils.cleanup_temp()


if __name__ == '__main__':
    main()
