import dearpygui.dearpygui as dpg
from multiprocessing import Process, Queue
import wx
from typing import Any

from flowtutor.flowchart.assignment import Assignment
from flowtutor.flowchart.call import Call
from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.declaration import Declaration
from flowtutor.flowchart.loop import Loop
from flowtutor.flowchart.input import Input
from flowtutor.flowchart.output import Output


class Modals:

    @staticmethod
    def show_approval_modal(label, message, callback):
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

    @staticmethod
    def show_input_text_modal(label, message, default_value, callback):
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

    @staticmethod
    def show_node_type_modal(callback, pos):
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
                    label='Loop',
                    width=-1,
                    callback=lambda: (callback(Loop()), dpg.delete_item('node_type_modal')))
                dpg.add_button(
                    label='Input',
                    width=-1,
                    callback=lambda: (callback(Input()), dpg.delete_item('node_type_modal')))
                dpg.add_button(
                    label='Output',
                    width=-1,
                    callback=lambda: (callback(Output()), dpg.delete_item('node_type_modal')))

    @staticmethod
    def show_open_modal(callback):
        def open(queue):
            app = wx.App(None)
            style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
            dialog = wx.FileDialog(None, 'Open', style=style)
            if dialog.ShowModal() == wx.ID_OK:
                path = dialog.GetPath()
            else:
                path = None
            dialog.Destroy()
            app.Destroy()
            ret = queue.get()
            ret['path'] = path
            queue.put(ret)
        queue: Any = Queue()
        ret = {'path': None}
        queue.put(ret)
        process = Process(target=open, args=(queue, ))
        process.start()
        process.join()
        callback(queue.get()['path'])

    @staticmethod
    def show_save_as_modal(callback):
        def save_as(queue):
            app = wx.App(None)
            style = wx.FD_SAVE
            dialog = wx.FileDialog(None, 'Save as...', style=style)
            if dialog.ShowModal() == wx.ID_OK:
                path = dialog.GetPath()
            else:
                path = None
            dialog.Destroy()
            app.Destroy()
            ret = queue.get()
            ret['path'] = path
            queue.put(ret)
        queue: Any = Queue()
        ret = {'path': None}
        queue.put(ret)
        process = Process(target=save_as, args=(queue, ))
        process.start()
        process.join()
        callback(queue.get()['path'])
