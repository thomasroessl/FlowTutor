import sys
from threading import Barrier
from bdb import Bdb
from io import StringIO
from typing import Any, Optional
from blinker import signal
from types import BuiltinFunctionType, BuiltinMethodType, FrameType, FunctionType, ModuleType

from flowtutor.debugger.stdinqueue import StdinQueue


class FtDb(Bdb):
    def __init__(self) -> None:
        super().__init__()
        self.output_stream = StringIO()
        self.error_stream = StringIO()
        self.input_stream: Any = StdinQueue()
        self.interacted = False
        self.barrier: Optional[Barrier] = None
        self.current_frame: Optional[FrameType] = None

    def read_output(self) -> None:
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
        sys.stdout = self.output_stream
        sys.stderr = self.error_stream
        sys.stdin = self.input_stream
        self.current_frame = frame
        self.read_output()
        if frame.f_code.co_filename.endswith('flowtutor.py'):
            signal('variables').send(self, variables=self.filter_locals(frame.f_locals))
        if self.break_here(frame) or self.interacted:
            signal('hit-line').send(self, line=int(frame.f_lineno))
            self.barrier = Barrier(2)
            self.barrier.wait()

    def user_exception(self, _: FrameType, exc_info: Any) -> None:
        sys.stderr = self.error_stream
        _, message, _ = exc_info
        print(message, file=sys.stderr)
        self.read_output()
        self.set_quit()

    def interact(self) -> None:
        self.read_output()
        if self.barrier and self.barrier.n_waiting == 1:
            self.barrier.wait()
        self.interacted = True

    def filter_locals(self, locals_dict: dict[str, Any]) -> dict[str, Any]:
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
