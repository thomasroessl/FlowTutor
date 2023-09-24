from __future__ import annotations
import sys
from os import path
from re import match
from blinker import signal
from threading import Thread
from typing import TYPE_CHECKING

from flowtutor.debugger.debugsession import DebugSession
from flowtutor.debugger.ftdb import FtDb

if TYPE_CHECKING:
    from flowtutor.gui.debugger import Debugger


class FtdbSession(DebugSession):
    def __init__(self, debugger: Debugger):
        super().__init__(debugger)
        self.ftdb = FtDb()
        self.source_path = path.join(self.utils.get_temp_dir(), 'flowtutor.py')

    def run(self) -> None:
        def t(self: FtdbSession) -> None:
            source = open(self.source_path).read()
            compiled_code = compile(source, self.source_path, 'exec')
            self.refresh_break_points(self.source_path)
            self.ftdb.run(compiled_code)
            self.ftdb.read_output()
            signal('program-finished').send(self)
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
        Thread(target=t, args=[self]).start()

    def cont(self) -> None:
        self.refresh_break_points(self.source_path)
        self.ftdb.read_output()
        self.ftdb.set_continue()
        self.ftdb.interact()

    def stop(self) -> None:
        self.ftdb.set_quit()
        self.ftdb.interact()

    def step(self) -> None:
        self.ftdb.set_step()
        self.ftdb.interact()

    def next(self) -> None:
        if self.ftdb.current_frame:
            self.ftdb.set_next(self.ftdb.current_frame)
        self.ftdb.interact()

    def refresh_break_points(self, source_path: str) -> None:
        self.ftdb.clear_all_breaks()
        with open(self.utils.get_break_points_path()) as break_points_file:
            for m in map(lambda l: match(r'break flowtutor.c:(\d+)', l), break_points_file.readlines()):
                if m:
                    print(self.ftdb.set_break(source_path, int(m.groups()[0])))
