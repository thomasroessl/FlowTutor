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
    '''Handles interaction with FtDb.'''

    def __init__(self, debugger: Debugger):
        super().__init__(debugger)
        self.ftdb = FtDb()
        '''A instance of the FlowTutor debugger.'''
        self.source_path = path.join(self.utils_service.get_temp_dir(), 'flowtutor.py')
        '''The path of the source code file, that is generated from the flowchart.'''

    def run(self, flowchart: Flowchart) -> None:
        # User interaction is handled from a seperate thread.
        def t(self: FtdbSession) -> None:
            source = open(self.source_path).read()
            try:
                # The generated source code is compiled to be run by FtDb.
                compiled_code = compile(source, self.source_path, 'exec')

                self.refresh_break_points(flowchart)
                self.ftdb.run(compiled_code)

                # Reads the output the is generated before the program is closed.
                self.ftdb.read_output()
            except SyntaxError as error:
                signal('program-error').send(self, error=f'{error.msg}\n{error.text}')
            except Exception:
                signal('program-error').send(self, error='Exception occured')

            signal('program-finished').send(self)

            # The default streams a restored after execution is finished.
            sys.stdout = sys.__stdout__
            sys.stdin = sys.__stdin__
            sys.stderr = sys.__stderr__
        Thread(target=t, args=[self]).start()

    def cont(self, flowchart: Flowchart) -> None:
        # Before continuing, refresh the break points, in case the user has altered them.
        self.refresh_break_points(flowchart)
        self.ftdb.read_output()
        self.ftdb.set_continue()
        self.ftdb.interact()

    def stop(self) -> None:
        self.ftdb.set_quit()
        self.ftdb.interact()

    def step(self, _: Flowchart) -> None:
        self.ftdb.set_step()
        self.ftdb.interact()

    def next(self, _: Flowchart) -> None:
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
