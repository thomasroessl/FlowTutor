from __future__ import annotations
from typing import TYPE_CHECKING
import re
import subprocess

if TYPE_CHECKING:
    from flowtutor.debugger import Debugger


class DebugSession:

    def __init__(self, debugger: Debugger):
        self.debugger = debugger

        # Start GDB, try to run the executable
        # and kill the process (bug workaround)
        gdb_init_process = subprocess.Popen(['gdb',
                                             '-q',
                                             'flowtutor.exe'],
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

        self._gdb_process = subprocess.Popen(['gdb',
                                              '-q',
                                              'flowtutor.exe'],
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

    def execute(self, command: str):
        if not self.process.stdin or not self.process.stdout:
            return
        self.process.stdin.write(f'{command}\n')
        for line in self.process.stdout:
            if (line == '(gdb)\n'):
                break
            elif re.search(r'Thread \d+ hit Breakpoint \d+', line):
                pass
            elif not re.search(r'\[New Thread .+\]', line)\
                    and not re.search(r'Starting program: .+', line)\
                    and not re.search(r'warning: unhandled dyld version .*', line):
                clean_line = re.sub(r'\[Inferior .+\]\n?', '', line)
                if len(clean_line) > 0:
                    self.debugger.log(clean_line)
                pass

    def run(self):
        self.execute('run')

    def stop(self):
        if self.process.stdout is None or self.process.stdin is None:
            return
        self.process.stdin.write('kill\n')
        for line in self.process.stdout:
            if (line == '(gdb)\n'):
                break
            elif re.search(r'Kill the program', line):
                self.process.stdin.write('y\n')
            elif re.search(r'\[Inferior .+\]', line):
                self.debugger.log(line)
            else:
                self.debugger.log(line)

    def step(self):
        self.execute('step')

    def next(self):
        self.execute('next')

    def get_variable_assignments(self):
        if self.process.stdout is None or self.process.stdin is None:
            return
        self.process.stdin.write('info locals\n')
        for line in self.process.stdout:
            if (line == '(gdb)\n'):
                break
            elif re.search(r'.+ = .+', line):
                self.debugger.log_debug(line)
            else:
                self.debugger.log(line)
                pass

    def set_break_point(self, line):
        if self.process.stdout is None or self.process.stdin is None:
            return
        self.process.stdin.write(f'break test.c:{line}\n')
        for line in self.process.stdout:
            if (line == '(gdb)\n'):
                break
            else:
                self.debugger.log_debug(line)
                pass
