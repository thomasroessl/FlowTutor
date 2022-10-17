from __future__ import annotations
import re
import subprocess


class DebugSession:

    def __init__(self):
        # Start GDB, try to run the executable
        # and kill the process (bug workaround)
        gdb_init_process = subprocess.Popen(['gdb',
                                             '-q',
                                             'flowtutor'],
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
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
                                              'flowtutor'],
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE,
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
                    and not re.search(r'\[Inferior .+\]', line)\
                    and not re.search(r'Starting program: .+', line):
                print(line, end='')
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
                print(line, end='')
            else:
                print(line, end='')

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
                print('VAR', line, end='')
            else:
                print(line, end='')
                pass

    def set_break_point(self, line):
        if self.process.stdout is None or self.process.stdin is None:
            return
        self.process.stdin.write(f'break test.c:{line}\n')
        for line in self.process.stdout:
            if (line == '(gdb)\n'):
                break
            else:
                print(line, end='')
                pass
