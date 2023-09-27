from __future__ import annotations
import sys
from os import path
from blinker import signal
from threading import Thread
from typing import TYPE_CHECKING

from flowtutor.debugger.debugsession import DebugSession
from flowtutor.debugger.ftdb import FtDb

if TYPE_CHECKING:
    from flowtutor.gui.debugger import Debugger
    from flowtutor.flowchart.flowchart import Flowchart


class FtdbSession(DebugSession):
    def __init__(self, debugger: Debugger):
        super().__init__(debugger)
        self.ftdb = FtDb()
        self.source_path = path.join(self.utils.get_temp_dir(), 'flowtutor.py')

    def run(self, flowchart: Flowchart) -> None:
        def t(self: FtdbSession) -> None:
            source = open(self.source_path).read()
            try:
                compiled_code = compile(source, self.source_path, 'exec')
                self.refresh_break_points(flowchart)
                self.ftdb.run(compiled_code)
                self.ftdb.read_output()
            except SyntaxError as error:
                signal('program-error').send(self, error=f'{error.msg}\n{error.text}')
            except Exception:
                signal('program-error').send(self, error='Exception occured')

            signal('program-finished').send(self)
            sys.stdout = sys.__stdout__
            sys.stdin = sys.__stdin__
            sys.stderr = sys.__stderr__
        Thread(target=t, args=[self]).start()

    def cont(self, flowchart: Flowchart) -> None:
        self.refresh_break_points(flowchart)
        self.ftdb.read_output()
        self.ftdb.set_continue()
        self.ftdb.interact()

    def stop(self) -> None:
        self.ftdb.set_quit()
        self.ftdb.interact()

    def step(self, flowchart: Flowchart) -> None:
        self.ftdb.set_step()
        self.ftdb.interact()

    def next(self, flowchart: Flowchart) -> None:
        if self.ftdb.current_frame:
            self.ftdb.set_next(self.ftdb.current_frame)
        self.ftdb.interact()

    def write(self, value: str) -> None:
        self.ftdb.input_stream.write(value)
        self.ftdb.read_output()

    def refresh_break_points(self, flowchart: Flowchart) -> None:
        self.ftdb.clear_all_breaks()
        for b in flowchart.break_points:
            self.ftdb.set_break(self.source_path, b)
