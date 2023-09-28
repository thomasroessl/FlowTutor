from __future__ import annotations
from re import search
from os import remove
from subprocess import PIPE, STDOUT, Popen
from threading import Thread
from sys import stderr
from typing import Optional
from pygdbmi import gdbmiparser
from blinker import signal
from typing import TYPE_CHECKING, cast

from flowtutor.debugger.debugsession import DebugSession

if TYPE_CHECKING:
    from flowtutor.gui.debugger import Debugger
    from flowtutor.flowchart.flowchart import Flowchart


class GdbSession(DebugSession):

    def __init__(self, debugger: Debugger):
        super().__init__(debugger)
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
        self._gdb_process = Popen(self.gdb_args,
                                  stdout=PIPE,
                                  stderr=STDOUT,
                                  stdin=PIPE,
                                  text=True,
                                  bufsize=1)

        if not self.process or not self.process.stdout or not self.process.stdin:
            return

        self.break_point_path = self.utils.get_break_points_path()

        for line in self.process.stdout:
            print('INIT', line, end='', file=stderr)
            if (search(r'\(gdb\)\s*$', line)):
                break

    def __del__(self) -> None:
        if not self._gdb_process:
            return
        self._gdb_process.kill()

    @property
    def process(self) -> Optional[Popen[str]]:
        return self._gdb_process

    def execute(self, command: str, flowchart: Flowchart) -> None:
        if not self.process:
            return

        def t(self: GdbSession) -> None:
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
                            self.cont(flowchart)
                        else:
                            self.get_variable_assignments()
                            signal('hit-line').send(self, line=int(frame['line']))
                    elif reason == 'signal-received':
                        meaning = record['payload']['signal-meaning']
                        signal('program-error').send(self, error=meaning)
                        signal('program-finished').send(self)
                    break
                elif record['message'] == 'error':
                    signal('program-finished').send(self)

            print('END EXECUTE:', command, file=stderr)
        Thread(target=t, args=[self]).start()

    def run(self, flowchart: Flowchart) -> None:
        self.refresh_break_points(flowchart)
        self.execute('-exec-run\n', flowchart)

    def cont(self, flowchart: Flowchart) -> None:
        self.refresh_break_points(flowchart)
        self.execute('-exec-continue', flowchart)

    def stop(self) -> None:
        if not self.process or not self.process.stdin:
            return
        self.process.stdin.write('kill\n')
        signal('program-finished').send(self)

    def step(self, flowchart: Flowchart) -> None:
        self.execute('-exec-step', flowchart)

    def next(self, flowchart: Flowchart) -> None:
        self.execute('-exec-next', flowchart)

    def refresh_break_points(self, flowchart: Flowchart) -> None:
        if not self.process or not self.process.stdin:
            return
        try:
            remove(self.break_point_path)
        except FileNotFoundError:
            pass
        break_point_definitions = '\n'.join(
            map(lambda line: f'break flowtutor.c:{line}', flowchart.break_points))

        with open(self.break_point_path, 'w') as file:
            file.write(break_point_definitions)
        self.process.stdin.write('-break-delete\n')
        self.process.stdin.write(f'source {self.utils.get_break_points_path()}\n')

    def write(self, value: str) -> None:
        self.utils.write_tty(value)

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
                    match = search(r'^\$1 = (.*)', payload.strip())
                    if match:
                        variables[var_name] = str(match.group(1))

        signal('variables').send(self, variables=variables)
