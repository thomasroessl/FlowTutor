import os
from typing import Union
import dearpygui.dearpygui as dpg

from flowtutor.flowchart_gui import FlowChartGUI
from flowtutor.flowchart.assignment import Assignment
from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.loop import Loop
from flowtutor.themes import create_theme_dark, create_theme_light

dpg.create_context()

flowchart: Union[FlowChartGUI, None] = None


def on_light_theme_menu_item_click():
    dpg.bind_theme(create_theme_light())
    if flowchart:
        flowchart.redraw_all()


def on_dark_theme_menu_item_click():
    dpg.bind_theme(create_theme_dark())
    if flowchart:
        flowchart.redraw_all()


def on_window_resize():
    if flowchart is not None:
        flowchart.parent_size = dpg.get_item_rect_size("flowchart_container")
        flowchart.resize()


with dpg.font_registry():
    deafault_font = dpg.add_font(os.path.join(os.path.dirname(__file__), "../../assets/inconsolata.ttf"), 18)
dpg.bind_font(deafault_font)

with dpg.viewport_menu_bar(tag="menu_bar"):
    with dpg.menu(label="File"):
        dpg.add_menu_item(label="Save")
        dpg.add_menu_item(label="Save As")
    with dpg.menu(label="View"):
        with dpg.menu(label="Theme"):
            dpg.add_menu_item(label="Light", callback=on_light_theme_menu_item_click)
            dpg.add_menu_item(label="Dark", callback=on_dark_theme_menu_item_click)
    with dpg.menu(label="Help"):
        dpg.add_menu_item(label="About")

with dpg.window(tag="main_window"):
    with dpg.group(tag="main_group", pos=[7, 30], horizontal=True):
        with dpg.child_window(width=217, label="Selected Node"):
            dpg.add_text("Selected Node:")
            dpg.add_text("None", tag="selected_node")

with dpg.item_handler_registry(tag="window_handler"):
    dpg.add_item_resize_handler(callback=on_window_resize)
dpg.bind_item_handler_registry("main_window", "window_handler")

dpg.configure_app()

dpg.create_viewport(title="FlowTutor")

dpg.bind_theme(create_theme_light())

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("main_window", True)

is_initialized = False

while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame()
    if not is_initialized:
        with dpg.child_window(tag="flowchart_container", parent="main_group", horizontal_scrollbar=True):
            flowchart = FlowChartGUI("flowchart", 1000, 1000)
            node1 = Assignment()
            node2 = Conditional()
            node3 = Loop()
            flowchart.add_node(node1, None)
            flowchart.add_node(node2, node1)
            flowchart.add_node(node3, node2)
            flowchart.redraw_all()
        is_initialized = True

dpg.destroy_context()
