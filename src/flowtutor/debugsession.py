from __future__ import annotations
from blinker import signal
from typing import TYPE_CHECKING, Optional, cast
from sys import stderr
import re
import subprocess
import threading
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
        self._gdb_process = None
        try:
            self.gdb_args = [self.utils.get_gdb_exe(),
                             '-q',
                             '-x',
                             self.utils.get_gdb_commands_path(),
                             '--interpreter=mi',
                             self.utils.get_exe_path()]
        except FileNotFoundError as error:
            self.debugger.log_error(str(error))
            return

        print('GDB ARGS', self.gdb_args, file=stderr)
        self._gdb_process = subprocess.Popen(self.gdb_args,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.STDOUT,
                                             stdin=subprocess.PIPE,
                                             text=True,
                                             bufsize=1)

        if not self.process or not self.process.stdout or not self.process.stdin:
            return

        for line in self.process.stdout:
            print('INIT', line, end='', file=stderr)
            if (re.search(r'\(gdb\)\s*$', line)):
                break

    def __del__(self) -> None:
        if not self._gdb_process:
            return
        self._gdb_process.kill()

    @property
    def process(self) -> Optional[subprocess.Popen[str]]:
        return self._gdb_process

    def execute(self, command: str) -> None:
        if not self.process:
            return

        def t(self: DebugSession) -> None:
            if not self.process or not self.process.stdin or not self.process.stdout:
                return
            print('START EXECUTE:', command, file=stderr)
            self.process.stdin.write(f'{command}\n')

            for line in self.process.stdout:
                if line.startswith('^error,msg="Unable to find Mach'):
                    self.process.kill()
                    self._gdb_process = None
                    self.debugger.log_error('GDB is not code-signed on this machine.')
                record = gdbmiparser.parse_response(line)
                print(f'EXECUTE {command}', record, file=stderr)
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
                            signal('hit-line').send(self, line=int(frame['line']) - 1)
                    elif reason == 'signal-received':
                        meaning = record['payload']['signal-meaning']
                        signal('program-error').send(self, error=meaning)
                        signal('program-finished').send(self)
                    break
                elif record['message'] == 'error':
                    signal('program-finished').send(self)

            print('END EXECUTE:', command, file=stderr)
        threading.Thread(target=t, args=[self]).start()

    def run(self) -> None:
        self.execute('-exec-run\n')

    def cont(self) -> None:
        self.refresh_break_points()
        self.execute('-exec-continue')

    def stop(self) -> None:
        if not self.process or not self.process.stdin:
            return
        self.process.stdin.write('kill\n')
        signal('program-finished').send(self)

    def step(self) -> None:
        self.execute('-exec-step')

    def next(self) -> None:
        self.execute('-exec-next')

    def refresh_break_points(self) -> None:
        if not self.process or not self.process.stdin:
            return
        self.process.stdin.write('-break-delete\n')
        self.process.stdin.write(f'source {self.utils.get_break_points_path()}\n')

    def get_variable_assignments(self) -> None:
        if not self.process or not self.process.stdout or not self.process.stdin:
            return
        variables: dict[str, str] = {}
        unknown_value_vars: list[str] = []
        self.process.stdin.write('-stack-list-locals --simple-values\n')
        for line in self.process.stdout:
            record = gdbmiparser.parse_response(line)
            print('VARIABLE_ASSIGNMENTS', record, file=stderr)
            if record['message'] == 'stopped':
                break
            elif record['type'] == 'result' and record['message'] == 'done':
                if record['payload']:
                    result_locals = record['payload']['locals']
                    if result_locals:
                        for var in result_locals:
                            if cast(str, var['type']).endswith('*'):
                                unknown_value_vars.append(f'*{var["name"]}')
                            elif 'value' in var:
                                variables[var['name']] = str(var['value'])
                            else:
                                unknown_value_vars.append(var['name'])
                        print('VARIABLE_ASSIGNMENTS', variables, file=stderr)
                    break
        for var_name in unknown_value_vars:
            self.process.stdin.write(f'print {var_name}\n')
            for line in self.process.stdout:
                record = gdbmiparser.parse_response(line)
                print(f'PRINT_VARIABLE {var_name}', record, file=stderr)
                if record['message'] == 'stopped':
                    break
                elif record['type'] == 'result' and record['message'] == 'done':
                    break
                elif record['type'] == 'console':
                    payload = str(record['payload'])
                    match = re.search(r'^\$1 = (.*)', payload.strip())
                    if match:
                        variables[var_name] = str(match.group(1))

        signal('variables').send(self, variables=variables)
