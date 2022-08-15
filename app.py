import dearpygui.dearpygui as dpg

from ftflowchart import FTFlowChart
from ftnodetype import FTNodeType

dpg.create_context()

flowchart = None

with dpg.font_registry():
    deafault_font = dpg.add_font("inconsolata.ttf", 18)
dpg.bind_font(deafault_font)

with dpg.viewport_menu_bar(tag="menu_bar"):
    with dpg.menu(label="File"):
        dpg.add_menu_item(label="Save")
        dpg.add_menu_item(label="Save As")
    with dpg.menu(label="Help"):
        dpg.add_menu_item(label="About")


with dpg.window(tag="main_window"):
    with dpg.group(tag="main_group", pos=[7, 30], horizontal=True):
        with dpg.child_window(width=217, label="Selected Node"):
            dpg.add_text("Selected Node:")
            dpg.add_text("None", tag="selected_node")
            pass

def on_window_resize():
    if flowchart is not None:
        flowchart.parent_size = dpg.get_item_rect_size("flowchart_container")
        flowchart.resize()

with dpg.item_handler_registry(tag="window_handler"):
    dpg.add_item_resize_handler(callback=on_window_resize)
dpg.bind_item_handler_registry("main_window", "window_handler")

dpg.create_viewport(title="FlowTutor")
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("main_window", True)

is_initialized = False

while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame()
    if not is_initialized:
        with dpg.child_window(tag="flowchart_container", parent="main_group", horizontal_scrollbar=True):
            flowchart = FTFlowChart("flowchart", 1000, 1000)
            shape1 = flowchart.add_node(FTNodeType.Assignment, [220, 20])
            shape2 = flowchart.add_node(FTNodeType.Conditional, [220, 170])
            shape3 = flowchart.add_node(FTNodeType.Loop, [95, 300])

            flowchart.add_connection(shape1, 0, shape2)
            flowchart.add_connection(shape2, 0, shape3)

        is_initialized = True

dpg.destroy_context()
