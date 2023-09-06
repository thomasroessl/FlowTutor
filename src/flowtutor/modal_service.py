from __future__ import annotations
import dearpygui.dearpygui as dpg
from multiprocessing import Process, Queue
from typing import TYPE_CHECKING, Any, Callable, Optional
import tkinter as tk
from tkinter import filedialog as fd
from dependency_injector.wiring import Provide, inject

from flowtutor.flowchart.template import Template

if TYPE_CHECKING:
    from flowtutor.language_service import LanguageService
    from flowtutor.util_service import UtilService
    from flowtutor.flowchart.flowchart import Flowchart
    from flowtutor.flowchart.node import Node


class ModalService:

    @inject
    def __init__(self,
                 utils_service: UtilService = Provide['utils_service'],
                 language_service: LanguageService = Provide['language_service']):
        self.language_service = language_service
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
                    dpg.add_input_text(default_value=self.utils_service.get_templates_path(''),
                                       width=-1,
                                       readonly=True)
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

    def show_welcome_modal(self,
                           language_selection_callback: Callable[[dict[str, Any]], None],
                           open: Callable[[], None]) -> None:
        if dpg.does_item_exist('welcome_modal'):
            return
        with dpg.window(
                label='Welcome',
                modal=True,
                tag='welcome_modal',
                autosize=True,
                no_close=True,
                no_collapse=True,
                pos=(250, 100),
                on_close=lambda: dpg.delete_item('welcome_modal')):
            with dpg.theme() as lang_button_theme:
                with dpg.theme_component(dpg.mvImageButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255), category=dpg.mvThemeCat_Core)
            dpg.add_text('New file:')
            with dpg.group():
                with dpg.group(horizontal=True):
                    for lang_id, data in self.language_service.get_languages().items():
                        if dpg.does_item_exist(f'{lang_id}_image'):
                            lang_button = dpg.add_image_button(
                                f'{lang_id}_image',
                                user_data=data,
                                callback=lambda s: (language_selection_callback(dpg.get_item_user_data(s)),
                                                    dpg.delete_item('welcome_modal')))
                            dpg.bind_item_theme(lang_button, lang_button_theme)
                        else:
                            dpg.add_button(
                                label=data['name'],
                                width=75,
                                user_data=data,
                                callback=lambda s: (language_selection_callback(dpg.get_item_user_data(s)),
                                                    dpg.delete_item('welcome_modal')))
                dpg.add_separator()
                dpg.add_button(
                    label='Open file',
                    width=-1,
                    callback=lambda: (dpg.delete_item('welcome_modal'), open()))

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

    def show_node_type_modal(self,
                             flowchart: Flowchart,
                             callback: Callable[[Node], None],
                             pos: tuple[int, int]) -> None:
        with dpg.window(
                label='Add Node',
                pos=pos,
                modal=True,
                tag='node_type_modal',
                no_resize=True,
                autosize=True,
                on_close=lambda: dpg.delete_item('node_type_modal')):
            with dpg.group():
                for label, args in self.language_service.get_node_templates(flowchart).items():
                    dpg.add_button(
                        label=label,
                        width=200,
                        user_data=args,
                        callback=lambda s: (user_data := dpg.get_item_user_data(s),
                                            callback(Template(user_data)),
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
