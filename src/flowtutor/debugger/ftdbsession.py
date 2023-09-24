from __future__ import annotations
from os import path
import sys
from blinker import signal
import threading
from typing import TYPE_CHECKING

from flowtutor.debugger.debugsession import DebugSession
from flowtutor.debugger.ftdb import FtDb

if TYPE_CHECKING:
    from flowtutor.gui.debugger import Debugger


class FtdbSession(DebugSession):
    def __init__(self, debugger: Debugger):
        super().__init__(debugger)
        self.ftdb = FtDb()

    def run(self) -> None:
        def t(self: FtdbSession) -> None:
            source_path = path.join(self.utils.get_temp_dir(), 'flowtutor.py')
            source = open(source_path).read()
            compiled_code = compile(source, source_path, 'exec')
            # TODO implement breakpoints
            # self.ftdb.set_break(source_path, 5)
            self.ftdb.run(compiled_code)
            self.ftdb.read_output()
            signal('program-finished').send(self)
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

        threading.Thread(target=t, args=[self]).start()

    def cont(self) -> None:
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
