import dearpygui.dearpygui as dpg

from flowtutor.gui import GUI


def main():
    GUI(2000, 2000)
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
