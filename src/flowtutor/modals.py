import dearpygui.dearpygui as dpg

from flowtutor.flowchart.assignment import Assignment
from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.loop import Loop
from flowtutor.flowchart.input import Input
from flowtutor.flowchart.output import Output


class Modals:

    @staticmethod
    def show_approval_modal(label, message, callback):
        with dpg.window(
                label=label,
                modal=True,
                tag="approval_modal",
                autosize=True,
                pos=(100, 100),
                on_close=lambda: dpg.delete_item("approval_modal")):
            dpg.add_text(message)
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="OK",
                    width=75,
                    callback=lambda: (callback(), dpg.delete_item("approval_modal")))
                dpg.add_button(
                    label="Cancel",
                    width=75,
                    callback=lambda: dpg.delete_item("approval_modal"))

    @staticmethod
    def show_node_type_modal(callback, pos):
        with dpg.window(
                label="Add Node",
                pos=pos,
                modal=True,
                tag="node_type_modal",
                width=150,
                no_resize=True,
                on_close=lambda: dpg.delete_item("node_type_modal")):
            with dpg.group():
                dpg.add_button(
                    label="Assignment",
                    width=-1,
                    callback=lambda: (callback(Assignment()), dpg.delete_item("node_type_modal")))
                dpg.add_button(
                    label="Conditional",
                    width=-1,
                    callback=lambda: (callback(Conditional()), dpg.delete_item("node_type_modal")))
                dpg.add_button(
                    label="Loop",
                    width=-1,
                    callback=lambda: (callback(Loop()), dpg.delete_item("node_type_modal")))
                dpg.add_button(
                    label="Input",
                    width=-1,
                    callback=lambda: (callback(Input()), dpg.delete_item("node_type_modal")))
                dpg.add_button(
                    label="Output",
                    width=-1,
                    callback=lambda: (callback(Output()), dpg.delete_item("node_type_modal")))
