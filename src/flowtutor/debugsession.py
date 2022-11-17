from __future__ import annotations
from blinker import signal
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

    def execute(self, command: str) -> bool:
        if not self.process.stdin or not self.process.stdout:
            return True
        self.process.stdin.write(f'{command}\n')
        finished = False
        hit_end = False
        for line in self.process.stdout:
            print(line.__repr__())
            if (line == '(gdb)\n'):
                break
            if (line == 'Continuing.\n') or\
                    re.search(r'\[New Thread .+\]', line) or\
                    re.search(r'Starting program: .+', line) or\
                    re.search(r'Kill the program being debugged\?.*', line) or\
                    re.search(r'warning: unhandled dyld version .*', line) or\
                    re.search(r'Thread \d+ hit Breakpoint \d+', line) or\
                    re.search(r'0x[A-Za-z0-9]+ in \?\? \(\)', line):
                pass
            elif (match := re.match(r'(\d+)\t.*', line)) is not None:
                if len(match.group(1)) > 0:
                    signal('hit-line').send(self, line=int(match.group(1)))
            elif re.search(r'Cannot find bounds of current function', line):
                hit_end = True
            elif (match := re.match(r'(.*)\[Inferior .+\]\n?', line)) is not None:
                finished = True
                if len(match.group(1)) > 0:
                    self.debugger.log(match.group(1))
            elif not line.isspace():
                self.debugger.log(line)
        if hit_end:
            return self.cont()
        else:
            if finished:
                signal('program-finished').send(self)
            return finished

    def run(self) -> bool:
        return self.execute('run')

    def cont(self) -> bool:
        return self.execute('continue')

    def stop(self):
        return self.execute('kill')

    def step(self) -> bool:
        return self.execute('step')

    def next(self) -> bool:
        return self.execute('next')

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
