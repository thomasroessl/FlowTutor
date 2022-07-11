from turtle import width
import dearpygui.dearpygui as dpg

from flowchart import FlowChart
from shapetype import ShapeType

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

def add_assignment():
    shape = flowchart.add_shape(ShapeType.Assignment, [220, flowchart.get_max_y() + 50])
    flowchart.add_connection(flowchart.shapes[-2], shape)
    flowchart.resize()

def add_conditional():
    shape = flowchart.add_shape(ShapeType.Conditional, [220, flowchart.get_max_y() + 50])
    flowchart.add_connection(flowchart.shapes[-2], shape)
    flowchart.resize()

def add_loop():
    shape = flowchart.add_shape(ShapeType.Loop, [220, flowchart.get_max_y() + 50])
    flowchart.add_connection(flowchart.shapes[-2], shape)
    flowchart.resize()

with dpg.window(tag="main_window"):
    with dpg.group(tag="main_group", pos=[7, 30], horizontal=True):
        with dpg.child_window(width=217):
            dpg.add_button(label="Assignment", width=200, callback=add_assignment)
            dpg.add_button(label="Conditional", width=200, callback=add_conditional)
            dpg.add_button(label="Loop", width=200, callback=add_loop)
            dpg.add_button(label="Input", width=200)
            dpg.add_button(label="Output", width=200)
        
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
            flowchart = FlowChart("flowchart", 1000, 1000)
            shape1 = flowchart.add_shape(ShapeType.Assignment, [220, 20])
            shape2 = flowchart.add_shape(ShapeType.Conditional, [220, 170])
            shape3 = flowchart.add_shape(ShapeType.Loop, [20, 340])

            flowchart.add_connection(shape1, shape2)
            flowchart.add_connection(shape2, shape3)

        is_initialized = True
        # with dpg.theme() as flowchart_container_theme:
        #     with dpg.theme_component(dpg.mvAll):
        #         dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (0, 0, 0), category=dpg.mvThemeCat_Core)
        # dpg.bind_item_theme("flowchart_container", flowchart_container_theme)

dpg.destroy_context()
