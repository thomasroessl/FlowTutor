from __future__ import annotations
import dearpygui.dearpygui as dpg
from multiprocessing import Process, Queue
from typing import Callable, Optional
import tkinter as tk
from tkinter import filedialog as fd
from dependency_injector.wiring import Provide, inject

from flowtutor.flowchart.node import Node
from flowtutor.nodes_service import NodesService
from flowtutor.util_service import UtilService


class ModalService:

    @inject
    def __init__(self,
                 utils_service: UtilService = Provide['utils_service'],
                 nodes_service: NodesService = Provide['nodes_service']):
        self.nodes_service = nodes_service
        self.utils_service = utils_service

    def show_paths_window(self) -> None:
        with dpg.window(
                label="FlowTutor",
                modal=True,
                tag='paths_window',
                width=600,
                height=-1,
                pos=(250, 100),
                on_close=lambda: dpg.delete_item('paths_window')):
            with dpg.table(
                    header_row=False,
                    borders_innerH=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_outerV=True):
                dpg.add_table_column(width_fixed=True, init_width_or_weight=120)
                dpg.add_table_column()
                with dpg.table_row():
                    dpg.add_text('FlowTutor')
                    dpg.add_input_text(default_value=self.utils_service.get_root_dir(), width=-1, readonly=True)
                with dpg.table_row():
                    dpg.add_text('GCC executable')
                    dpg.add_input_text(default_value=self.utils_service.get_gcc_exe(), width=-1, readonly=True)
                with dpg.table_row():
                    dpg.add_text('GDB executable')
                    dpg.add_input_text(default_value=self.utils_service.get_gdb_exe(), width=-1, readonly=True)
                with dpg.table_row():
                    dpg.add_text('Templates')
                    dpg.add_input_text(default_value=self.utils_service.get_templates_path(), width=-1, readonly=True)
                with dpg.table_row():
                    dpg.add_text('Source File')
                    dpg.add_input_text(default_value=self.utils_service.get_c_source_path(), width=-1, readonly=True)

    def show_approval_modal(self, label: str, message: str, callback: Callable[[], None]) -> None:
        with dpg.window(
                label=label,
                modal=True,
                tag='approval_modal',
                autosize=True,
                pos=(250, 100),
                on_close=lambda: dpg.delete_item('approval_modal')):
            dpg.add_text(message)
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label='OK',
                    width=75,
                    callback=lambda: (callback(), dpg.delete_item('approval_modal')))
                dpg.add_button(
                    label='Cancel',
                    width=75,
                    callback=lambda: dpg.delete_item('approval_modal'))

    def show_input_text_modal(self,
                              label: str,
                              message: str,
                              default_value: str,
                              callback: Callable[[str], None]) -> None:
        with dpg.window(
                label=label,
                modal=True,
                tag='input_text_modal',
                autosize=True,
                pos=(250, 100),
                on_close=lambda: dpg.delete_item('input_text_modal')):
            dpg.add_text(message)
            dpg.add_input_text(tag='input_text', default_value=default_value)
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label='OK',
                    width=75,
                    callback=lambda: (callback(dpg.get_value('input_text')), dpg.delete_item('input_text_modal')))
                dpg.add_button(
                    label='Cancel',
                    width=75,
                    callback=lambda: dpg.delete_item('input_text_modal'))

    def show_node_type_modal(self, callback: Callable[[Node], None], pos: tuple[int, int]) -> None:
        with dpg.window(
                label='Add Node',
                pos=pos,
                modal=True,
                tag='node_type_modal',
                width=150,
                no_resize=True,
                on_close=lambda: dpg.delete_item('node_type_modal')):
            with dpg.group():

                for label, node_class, args in self.nodes_service.get_node_types():
                    dpg.add_button(
                        label=label,
                        width=-1,
                        user_data=(node_class, args),
                        callback=lambda s: (user_data := dpg.get_item_user_data(s),
                                            callback(user_data[0](user_data[1]) if user_data[1] else user_data[0]()),
                                            dpg.delete_item('node_type_modal')))

    def open(self, queue: Queue[dict[str, Optional[str]]]) -> None:
        tk_root = tk.Tk()
        tk_root.withdraw()
        path = fd.askopenfilename(
            title='Open...',
            defaultextension='*.flowtutor',
            filetypes=[('FlowTutor Files', '*.flowtutor')]
        )
        tk_root.destroy()
        ret = queue.get()
        ret['path'] = path
        queue.put(ret)

    def show_open_modal(self, callback: Callable[[str], None]) -> None:
        queue: Queue[dict[str, Optional[str]]] = Queue()
        ret: dict[str, Optional[str]] = {'path': None}
        queue.put(ret)
        process = Process(target=self.open, args=(queue, ))
        process.start()
        process.join()
        path = queue.get()['path']
        if path:
            callback(path)

    def save_as(self, queue: Queue[dict[str, Optional[str]]]) -> None:
        tk_root = tk.Tk()
        tk_root.withdraw()
        path = fd.asksaveasfilename(
            title='Save As...',
            defaultextension='*.flowtutor',
            filetypes=[('FlowTutor Files', '*.flowtutor')]
        )
        tk_root.destroy()
        ret = queue.get()
        ret['path'] = path
        queue.put(ret)

    def show_save_as_modal(self, callback: Callable[[str], None]) -> None:
        queue: Queue[dict[str, Optional[str]]] = Queue()
        ret: dict[str, Optional[str]] = {'path': None}
        queue.put(ret)
        process = Process(target=self.save_as, args=(queue, ))
        process.start()
        process.join()
        path = queue.get()['path']
        if path:
            callback(path)
