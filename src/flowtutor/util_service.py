import sys
import platform
import pathlib
import os
import select
import threading

try:
    import termios
    import pty
except ModuleNotFoundError:
    pass

from blinker import signal
from shutil import which, rmtree
from tempfile import mkdtemp
from os import path


class UtilService:

    def __init__(self):
        self.root = pathlib.Path(sys.modules['__main__'].__file__ or '').parent.resolve()
        self.temp_dir = mkdtemp(None, 'flowtutor-')
        print(self.temp_dir)
        self.tty_name = ''
        self.tty_fd = 0
        self.is_stopped = threading.Event()

    def cleanup_temp(self):
        '''Deletes the temporary working directory.'''
        rmtree(self.temp_dir)

    def get_root_dir(self):
        '''Gets the root directory of the application.'''
        return self.root

    def get_gcc_exe(self):
        '''Gets the path to the installed gcc, or the packaged version of mingw on Windows.'''
        if (exe := which('gcc-12')) is not None:
            return exe
        elif (exe := which('gcc')) is not None:
            return exe
        elif platform.system() == 'Windows':
            return path.join(self.root, 'mingw64', 'bin', 'gcc.exe')
        else:
            raise FileNotFoundError('gcc could not be found on the system!')

    def get_gdb_exe(self):
        '''Gets the path to the installed gdb, or the packaged version of mingw on Windows.'''
        if (exe := which('gdb')) is not None:
            return exe
        elif platform.system() == 'Windows':
            return path.join(self.root, 'mingw64', 'bin', 'gdb.exe')
        else:
            raise FileNotFoundError('gdb could not be found on the system!')

    def get_exe_path(self):
        '''Gets the path to the executable compiled by flowtutor (through gcc).'''
        return path.join(self.temp_dir, 'flowtutor.exe')

    def get_gdb_commands_path(self):
        '''Creates and gets the path to the command file used for starting gdb.'''
        gdb_commands_path = path.join(self.temp_dir, 'gdb_commands')
        gdb_commands = 'set prompt (gdb)\\n'

        # The following command is needed for gdb to run on MacOS with System Integrity Protection
        if platform.system() == 'Darwin':
            gdb_commands += '\nset startup-with-shell off'

        if platform.system() == 'Windows':
            gdb_commands += '\nset new-console on'
        else:
            gdb_commands += f'\ntty {self.tty_name}'

        gdb_commands += f'\nsource {self.get_break_points_path()}'
        with open(gdb_commands_path, 'w') as gdb_commands_file:
            gdb_commands_file.write(gdb_commands)
        return gdb_commands_path

    def get_c_source_path(self):
        '''Gets the path to the generated C-source code of the flowchart.'''
        return path.join(self.temp_dir, 'flowtutor.c')

    def get_break_points_path(self):
        '''Gets the path to the break-point file for gdb.'''
        return path.join(self.temp_dir, 'flowtutor_break_points')

    def open_tty(self):
        '''Opens a pseudoterminal for communication with gdb.'''

        if (os.isatty(sys.stdin.fileno())):
            attrs = termios.tcgetattr(sys.stdin)
            attrs[3] = attrs[3] & ~(termios.ISIG | termios.ICANON | termios.ECHO)
            termios.tcsetattr(sys.stdin, termios.TCSANOW, attrs)

        self.tty_fd, slave_fd = pty.openpty()
        self.tty_name = os.ttyname(slave_fd)

        def output(fd):
            while not self.is_stopped.is_set():
                rfds, _, _ = select.select([fd], [], [])
                if fd in rfds:
                    data = os.read(fd, 1)
                    if len(data) > 0:
                        try:
                            signal('recieve_output').send(self, output=data.decode('utf-8'))
                        except UnicodeDecodeError:
                            pass

        threading.Thread(target=output, args=[self.tty_fd]).start()

    def write_tty(self, message: str):
        '''Writes to the opened pseudoterminal that communicates with with gdb.'''
        os.write(self.tty_fd, (message + '\n').encode('utf-8'))

    def stop_tty(self):
        '''Stops the pseudoterminal thread.'''
        self.is_stopped.set()
        try:
            os.write(self.tty_fd, '\n'.encode('utf-8'))
        except OSError:
            pass  # Ignore error if tty has been stopped already
