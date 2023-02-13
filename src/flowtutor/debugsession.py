from __future__ import annotations
from blinker import signal
from typing import TYPE_CHECKING, Dict
import re
import platform
import subprocess
from pygdbmi import gdbmiparser
from dependency_injector.wiring import Provide, inject

from flowtutor.util_service import UtilService

if TYPE_CHECKING:
    from flowtutor.gui.debugger import Debugger


class DebugSession:

    @inject
    def __init__(self, debugger: Debugger, utils_service: UtilService = Provide['utils_service']):
        self.debugger = debugger
        self.utils = utils_service
        self.gdb_args = [self.utils.get_gdb_exe(),
                         '-q',
                         '-x',
                         self.utils.get_gdb_commands_path(),
                         '--interpreter=mi',
                         self.utils.get_exe_path()]

        if platform.system() == 'Darwin':
            # Start GDB, try to run the executable
            # and kill the process (bug workaround)
            gdb_init_process = subprocess.Popen(self.gdb_args,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT,
                                                stdin=subprocess.PIPE,
                                                text=True,
                                                bufsize=1)

            if gdb_init_process.stdout is None or gdb_init_process.stdin is None:
                return

            for line in gdb_init_process.stdout:
                print('INIT', line, end='')
                if (re.search(r'\(gdb\)\s*$', line)):
                    gdb_init_process.stdin.write('-exec-run\n')
                elif line.startswith('~"[New Thread'):
                    gdb_init_process.kill()
                    break

        self._gdb_process = subprocess.Popen(self.gdb_args,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.STDOUT,
                                             stdin=subprocess.PIPE,
                                             text=True,
                                             bufsize=1)
        if self.process.stdout is None or self.process.stdin is None:
            return

        for line in self.process.stdout:
            print('INIT', line, end='')
            if (re.search(r'\(gdb\)\s*$', line)):
                break

    def __del__(self):
        self._gdb_process.kill()

    @property
    def process(self) -> subprocess.Popen[str]:
        return self._gdb_process

    def execute(self, command: str) -> None:
        if not self.process.stdin or not self.process.stdout:
            return
        print('START EXECUTE:', command)
        self.process.stdin.write(f'{command}\n')

        for line in self.process.stdout:
            record = gdbmiparser.parse_response(line)
            print(f'EXECUTE {command}', record)
            if record['message'] == 'stopped':
                reason = record['payload']['reason']
                if reason == 'exited-normally':
                    signal('program-finished').send(self)
                elif reason == 'breakpoint-hit' or reason == 'end-stepping-range':
                    frame = record['payload']['frame']
                    if frame['func'] == '??':
                        self.cont()
                    else:
                        self.get_variable_assignments()
                        signal('hit-line').send(self, line=int(frame['line']))
                break
        print('END EXECUTE:', command)

    def run(self) -> None:
        self.execute('-exec-run\n')

    def cont(self) -> None:
        self.refresh_break_points()
        self.execute('-exec-continue')

    def stop(self):
        if not self.process.stdin:
            return
        self.process.stdin.write('kill\n')
        signal('program-finished').send(self)

    def step(self) -> None:
        self.execute('-exec-step')

    def next(self) -> None:
        self.execute('-exec-next')

    def refresh_break_points(self) -> None:
        if not self.process.stdin:
            return
        self.process.stdin.write('-break-delete\n')
        self.process.stdin.write(f'source {self.utils.get_break_points_path()}\n')

    def get_variable_assignments(self) -> None:
        if self.process.stdout is None or self.process.stdin is None:
            return
        variables: Dict[str, str] = {}
        self.process.stdin.write('-stack-list-locals --simple-values\n')
        for line in self.process.stdout:
            record = gdbmiparser.parse_response(line)
            print('VARIABLE_ASSIGNMENTS', record)
            if record['message'] == 'stopped':
                break
            elif record['type'] == 'result' and record['payload'] is not None:
                result_locals = record['payload']['locals']
                if result_locals is not None:
                    for var in result_locals:
                        variables[var['name']] = str(var['value'])
                    print('VARIABLE_ASSIGNMENTS', variables)
                    break
        signal('variables').send(self, variables=variables)

    def set_break_point(self, line) -> None:
        if self.process.stdout is None or self.process.stdin is None:
            return
        self.process.stdin.write(f'-break-insert --source flowtutor.c --line {line}\n')
