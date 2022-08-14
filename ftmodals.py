import dearpygui.dearpygui as dpg


class FTModals:

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
    def show_node_type_modal(assignment_callback, conditional_callback, loop_callback, input_callback, output_callback, pos):
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
                    callback=lambda: (assignment_callback(), dpg.delete_item("node_type_modal")))
                dpg.add_button(
                    label="Conditional",
                    callback=lambda: (conditional_callback(), dpg.delete_item("node_type_modal")))
                dpg.add_button(
                    label="Loop",
                    callback=lambda: (loop_callback(), dpg.delete_item("node_type_modal")))
                dpg.add_button(
                    label="Input",
                    callback=lambda: (input_callback(), dpg.delete_item("node_type_modal")))
                dpg.add_button(
                    label="Output",
                    callback=lambda: (output_callback(), dpg.delete_item("node_type_modal")))
