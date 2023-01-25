from __future__ import annotations
import sys
from blinker import signal
from typing import TYPE_CHECKING, Dict
import re
import subprocess
from flowtutor.utils import Utils

if TYPE_CHECKING:
    from flowtutor.debugger import Debugger


class DebugSession:

    def __init__(self, debugger: Debugger):
        self.debugger = debugger
        self.utils = Utils()
        self.gdb_args = [self.utils.get_gdb_exe(),
                         '-q',
                         '-x',
                         self.utils.get_gdb_commands_path(),
                         self.utils.get_exe_path()]

        print(self.gdb_args, file=sys.stderr)

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
            if (line == '(gdb)\n'):
                gdb_init_process.stdin.write('run\n')
            elif re.search(r'^Starting program: .+', line):
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
            if (line == '(gdb)\n'):
                break

    def __del__(self):
        self._gdb_process.kill()

    @property
    def process(self) -> subprocess.Popen[str]:
        return self._gdb_process

    def execute(self, command: str) -> None:
        if not self.process.stdin or not self.process.stdout:
            return
        self.process.stdin.write(f'{command}\n')
        hit_end = False
        hit_break_point = command == 'next' or command == 'step'
        for line in self.process.stdout:
            print(f'execute ({command}): {line.__repr__()}')
            if (line == '(gdb)\n'):
                if hit_break_point and not hit_end:
                    # Turn off stdout buffering
                    self.execute('call fix_debug()')
                    self.get_variable_assignments()
                break
            elif (match := re.match(r'(\d+)\t.*', line)) is not None and len(match.group(1)) > 0:
                signal('hit-line').send(self, line=int(match.group(1)))
            elif (line == 'Continuing.\n') or\
                    re.search(r'\[New Thread .+\]', line) or\
                    re.search(r'\[Thread .+\ exited with code .+]', line) or\
                    re.search(r'Starting program: .+', line) or\
                    re.search(r'Kill the program being debugged\?.*', line) or\
                    re.search(r'Delete all breakpoints\?.*', line) or\
                    re.search(r'Breakpoint \d at 0x[0-9a-f]+', line) or\
                    re.search(r'warning: unhandled dyld version .*', line):
                pass
            elif re.search(r'Thread \d+ hit Breakpoint \d+', line):
                hit_break_point = True
            elif re.search(r'Cannot find bounds of current function', line) or\
                    re.search(r'0x[0-9a-f]+ in \?\? \(\)', line) or\
                    re.search(r'0x[0-9a-f]+ in __tmainCRTStartup \(\)', line):
                hit_end = True
            elif (match := re.match(r'(.*)\[Inferior .+\]\n?', line)) is not None:
                if len(match.group(1)) > 0:
                    self.debugger.log(match.group(1))
                signal('program-finished').send(self)
            elif not line.isspace():
                self.debugger.log(line)
        if hit_end:
            self.cont()

    def run(self) -> None:
        self.execute('run')

    def cont(self) -> None:
        self.refresh_break_points()
        self.execute('continue')

    def stop(self):
        self.execute('kill')

    def step(self) -> None:
        self.execute('step')

    def next(self) -> None:
        self.execute('next')

    def refresh_break_points(self) -> None:
        self.execute('delete')
        self.execute(f'source {self.utils.get_break_points_path()}')

    def get_variable_assignments(self) -> None:
        if self.process.stdout is None or self.process.stdin is None:
            return
        variables: Dict[str, str] = {}
        self.process.stdin.write('info locals\n')
        for line in self.process.stdout:
            print(f'get_variable_assignments: {line.__repr__()}')
            if (line == '(gdb)\n'):
                signal('variables').send(self, variables=variables)
                break
            elif re.search(r'No locals\.', line):
                pass
            elif re.search(r'No symbol table info available\.', line):
                self.execute('continue')
                break
            elif match := re.search(r'(.+) = (.+)', line):
                variables[match.group(1)] = match.group(2)
            else:
                self.debugger.log(line)
                pass

    def set_break_point(self, line) -> None:
        if self.process.stdout is None or self.process.stdin is None:
            return
        self.process.stdin.write(f'break test.c:{line}\n')
        for line in self.process.stdout:
            if (line == '(gdb)\n'):
                break
            else:
                self.debugger.log_debug(line)
                pass
