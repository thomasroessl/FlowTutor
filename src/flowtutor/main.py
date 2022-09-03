import dearpygui.dearpygui as dpg

from flowtutor.gui import GUI
from flowtutor.flowchart.assignment import Assignment
from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.loop import Loop


def main():
    gui = GUI("flowchart", 2000, 2000)
    node1 = Assignment()
    node2 = Conditional()
    node3 = Loop()
    gui.flowchart.add_node(node1, None)
    gui.flowchart.add_node(node2, node1)
    gui.flowchart.add_node(node3, node2)
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
