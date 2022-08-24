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
                label="Node Type",
                pos=pos,
                modal=True,
                tag="node_type_modal",
                autosize=True,
                on_close=lambda: dpg.delete_item("node_type_modal")):
            with dpg.group():
                dpg.add_button(
                    label="Assignment",
                    callback=lambda: (callback(Assignment()), dpg.delete_item("node_type_modal")))
                dpg.add_button(
                    label="Conditional",
                    callback=lambda: (callback(Conditional()), dpg.delete_item("node_type_modal")))
                dpg.add_button(
                    label="Loop",
                    callback=lambda: (callback(Loop()), dpg.delete_item("node_type_modal")))
                dpg.add_button(
                    label="Input",
                    callback=lambda: (callback(Input()), dpg.delete_item("node_type_modal")))
                dpg.add_button(
                    label="Output",
                    callback=lambda: (callback(Output()), dpg.delete_item("node_type_modal")))
