import sys
from threading import Barrier
from bdb import Bdb
from io import StringIO
from typing import Any, Optional
from blinker import signal
from types import BuiltinFunctionType, BuiltinMethodType, FrameType, FunctionType, ModuleType

from flowtutor.debugger.stdinqueue import StdinQueue


class FtDb(Bdb):
    '''FtDb (FlowTutor-Debugger) class that implements the generic Python debugger base class.

    This class handles userinteraction with trace facility provided by Bdb.
    '''

    def __init__(self) -> None:
        super().__init__()
        self.output_stream = StringIO()
        '''This stream overrides sys.stdout to capture debugger output.'''
        self.error_stream = StringIO()
        '''This stream overrides sys.stderr to capture debugger errors.'''
        self.input_stream: StdinQueue = StdinQueue()
        '''This stream overrides sys.stdin to enable user input to the debugger.'''
        self.interacted = False
        '''True if the user has interacted with the debugger.'''
        self.barrier: Optional[Barrier] = None
        '''The barrier used to wait for user interaction.'''
        self.current_frame: Optional[FrameType] = None
        '''The frame the debugger is on currently.'''

    def read_output(self) -> None:
        '''Reads the output from the output- and error-streams and emits them as signals.'''
        output = self.output_stream.getvalue()
        self.output_stream.flush()
        self.output_stream.truncate(0)
        self.output_stream.seek(0)
        if output:
            signal('recieve-output').send(self, output=output)

        error = self.error_stream.getvalue()
        self.error_stream.flush()
        self.error_stream.truncate(0)
        self.error_stream.seek(0)
        if error:
            signal('program-error').send(self, error=error)

    def user_line(self, frame: FrameType) -> None:
        # Overrides the default streams with class instance, so the output of the debugged program can be captured.
        sys.stdout = self.output_stream
        sys.stderr = self.error_stream
        sys.stdin = self.input_stream  # type: ignore
        self.current_frame = frame

        # Reads output the occured before the current line.
        self.read_output()

        # If the frame comes from the debugged program, then emit a signal containing the local variables.
        if frame.f_code.co_filename.endswith('flowtutor.py'):
            signal('variables').send(self, variables=self.filter_locals(frame.f_locals))

        # If there is a break point on the line, or the user is stepping to it, then emit a signal with the line number.
        if self.break_here(frame) or self.interacted:
            signal('hit-line').send(self, line=int(frame.f_lineno))

            # Wait for user interaction.
            self.barrier = Barrier(2)
            self.barrier.wait()

    def user_exception(self, _: FrameType, exc_info: Any) -> None:
        sys.stderr = self.error_stream
        _, message, _ = exc_info
        print(message, file=sys.stderr)
        self.read_output()
        self.set_quit()

    def interact(self) -> None:
        '''This method is called, when the user interacts with the debugger.'''
        self.read_output()
        if self.barrier and self.barrier.n_waiting == 1:
            self.barrier.wait()
        self.interacted = True

    def filter_locals(self, locals_dict: dict[str, Any]) -> dict[str, Any]:
        '''Filter local system variables, that are not relevant to the user in the FlowTutor debugger.'''
        exclude_keys = ['copyright',
                        'credits',
                        'False',
                        'True',
                        'None',
                        'Ellipsis',
                        'quit',
                        'annotations',
                        'TYPE_CHECKING',
                        'Provide',
                        'Container',
                        'GUI',
                        'start']
        exclude_valuetypes = [BuiltinFunctionType,
                              BuiltinMethodType,
                              ModuleType,
                              FunctionType]
        return {k: v for k, v in locals_dict.items() if not (k in exclude_keys or type(v) in exclude_valuetypes)
                and k[0] != '_'}
