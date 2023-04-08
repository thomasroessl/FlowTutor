import dearpygui.dearpygui as dpg
from multiprocessing import Process, Queue
from typing import Any
import tkinter as tk
from tkinter import filedialog as fd

from flowtutor.flowchart.assignment import Assignment
from flowtutor.flowchart.call import Call
from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.declaration import Declaration
from flowtutor.flowchart.dowhileloop import DoWhileLoop
from flowtutor.flowchart.forloop import ForLoop
from flowtutor.flowchart.input import Input
from flowtutor.flowchart.output import Output
from flowtutor.flowchart.snippet import Snippet
from flowtutor.flowchart.whileloop import WhileLoop


class ModalService:

    def show_approval_modal(self, label, message, callback):
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

    def show_input_text_modal(self, label, message, default_value, callback):
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

    def show_node_type_modal(self, callback, pos):
        with dpg.window(
                label='Add Node',
                pos=pos,
                modal=True,
                tag='node_type_modal',
                width=150,
                no_resize=True,
                on_close=lambda: dpg.delete_item('node_type_modal')):
            with dpg.group():
                dpg.add_button(
                    label='Assignment',
                    width=-1,
                    callback=lambda: (callback(Assignment()), dpg.delete_item('node_type_modal')))
                dpg.add_button(
                    label='Call',
                    width=-1,
                    callback=lambda: (callback(Call()), dpg.delete_item('node_type_modal')))
                dpg.add_button(
                    label='Declaration',
                    width=-1,
                    callback=lambda: (callback(Declaration()), dpg.delete_item('node_type_modal')))
                dpg.add_button(
                    label='Conditional',
                    width=-1,
                    callback=lambda: (callback(Conditional()), dpg.delete_item('node_type_modal')))
                dpg.add_button(
                    label='For Loop',
                    width=-1,
                    callback=lambda: (callback(ForLoop()), dpg.delete_item('node_type_modal')))
                dpg.add_button(
                    label='While Loop',
                    width=-1,
                    callback=lambda: (callback(WhileLoop()), dpg.delete_item('node_type_modal')))
                dpg.add_button(
                    label='Do-While Loop',
                    width=-1,
                    callback=lambda: (callback(DoWhileLoop()), dpg.delete_item('node_type_modal')))
                dpg.add_button(
                    label='Input',
                    width=-1,
                    callback=lambda: (callback(Input()), dpg.delete_item('node_type_modal')))
                dpg.add_button(
                    label='Output',
                    width=-1,
                    callback=lambda: (callback(Output()), dpg.delete_item('node_type_modal')))
                dpg.add_button(
                    label='Code Snippet',
                    width=-1,
                    callback=lambda: (callback(Snippet()), dpg.delete_item('node_type_modal')))

    def open(self, queue):
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

    def show_open_modal(self, callback):
        queue: Any = Queue()
        ret = {'path': None}
        queue.put(ret)
        process = Process(target=self.open, args=(queue, ))
        process.start()
        process.join()
        path = queue.get()['path']
        if path:
            callback(path)

    def save_as(self, queue):
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

    def show_save_as_modal(self, callback):
        queue: Any = Queue()
        ret = {'path': None}
        queue.put(ret)
        process = Process(target=self.save_as, args=(queue, ))
        process.start()
        process.join()
        path = queue.get()['path']
        if path:
            callback(path)
