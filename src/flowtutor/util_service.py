from pathlib import Path
from platform import system
from select import select
from sys import modules, stdin
from threading import Event, Thread
from blinker import signal
from shutil import which, rmtree
import tempfile
from os import path, read, write
import dearpygui.dearpygui as dpg

try:
    import termios
    import pty
    from os import ttyname, isatty
except ModuleNotFoundError:
    pass


class UtilService:
    '''A service for miscellaneous utils.'''

    def __init__(self) -> None:
        self.root = Path(modules['__main__'].__file__ or '').parent.resolve()
        '''THe root directory of the application.'''
        self.temp_dir = tempfile.mkdtemp(None, 'flowtutor-')
        '''The working directory of the application.'''
        print(self.temp_dir)
        self.tty_name = ''
        '''The name of the TTY used for subprocess communication.'''
        self.tty_fd: int = 0
        '''The file descriptor of the TTY used for subprocess communication.'''
        self.is_stopped = Event()
        '''Gets set if the TTY thread gets stopped.'''
        self.is_windows = system() == 'Windows'
        '''True if the OS is Windows.'''
        self.is_mac_os = system() == 'Darwin'
        '''True if the OS is MacOS.'''

    def cleanup_temp(self) -> None:
        '''Deletes the temporary working directories.'''
        parent = Path(self.temp_dir).parent
        for d in parent.glob('flowtutor-*'):
            rmtree(d)

    def get_root_dir(self) -> Path:
        '''Gets the root directory of the application.'''
        return self.root

    def get_temp_dir(self) -> Path:
        '''Gets the temp directory where output files are stored.'''
        return Path(self.temp_dir)

    def get_gcc_exe(self) -> str:
        '''Gets the path to the installed gcc, or the packaged version of mingw on Windows.'''
        if exe := which('gcc-13'):
            return exe
        elif exe := which('gcc-12'):
            return exe
        elif exe := which('gcc'):
            return exe
        elif self.is_windows:
            return path.join(self.root, 'mingw64', 'bin', 'gcc.exe')
        else:
            raise FileNotFoundError('GCC could not be found on the system!')

    def get_gdb_exe(self) -> str:
        '''Gets the path to the installed gdb, or the packaged version of mingw on Windows.'''
        if exe := which('gdb'):
            return exe
        elif self.is_windows:
            return path.join(self.root, 'mingw64', 'bin', 'gdb.exe')
        else:
            raise FileNotFoundError('GDB could not be found on the system!')

    def get_exe_path(self) -> str:
        '''Gets the path to the executable compiled by flowtutor (through gcc).'''
        return path.join(self.temp_dir, 'flowtutor.exe')

    def get_gdb_commands_path(self) -> str:
        '''Creates and gets the path to the command file used for starting gdb.'''
        gdb_commands_path = path.join(self.temp_dir, 'gdb_commands')
        gdb_commands = 'set prompt (gdb)\\n'

        # The following command is needed for gdb to run on MacOS with System Integrity Protection
        if self.is_mac_os:
            gdb_commands += '\nset startup-with-shell off'

        if self.is_windows:
            gdb_commands += '\nset new-console on'
        else:
            gdb_commands += f'\ntty {self.tty_name}'

        gdb_commands += f'\nsource {self.get_break_points_path()}'
        with open(gdb_commands_path, 'w') as gdb_commands_file:
            gdb_commands_file.write(gdb_commands)
        return gdb_commands_path

    def get_source_path(self, file_ext: str) -> str:
        '''Gets the path to the generated source code file of the flowchart.

        Parameters:
            file_ext (str): The file extension of the source code file.
        '''
        return path.join(self.temp_dir, f'flowtutor{file_ext}')

    def get_break_points_path(self) -> str:
        '''Gets the path to the break-point file for gdb.'''
        return path.join(self.temp_dir, 'flowtutor_break_points')

    def get_templates_path(self, lang_id: str = '') -> str:
        '''Gets the path to the directory containing templates for predefined nodes.

        Parameters:
            lang_id (str): The identifier of the selected language.
        '''
        if (modules['__main__'].__file__ or '').endswith('.pyw'):
            result = path.join(self.root, 'templates', lang_id)
        else:
            result = path.abspath(path.join(self.root, '..', '..', 'templates', lang_id))
        return result

    def open_tty(self) -> None:
        '''Opens a pseudoterminal for communication with gdb.'''

        if (isatty(stdin.fileno())):
            attrs = termios.tcgetattr(stdin)
            attrs[3] = attrs[3] & ~(termios.ISIG | termios.ICANON | termios.ECHO)
            termios.tcsetattr(stdin, termios.TCSANOW, attrs)

        self.tty_fd, slave_fd = pty.openpty()
        self.tty_name = ttyname(slave_fd)

        def output(fd: int) -> None:
            while not self.is_stopped.is_set():
                rfds, _, _ = select([fd], [], [])
                if fd in rfds:
                    data = read(fd, 1)
                    if len(data) > 0:
                        try:
                            signal('recieve-output').send(self, output=data.decode('utf-8'))
                        except UnicodeDecodeError:
                            pass

        Thread(target=output, args=[self.tty_fd]).start()

    def write_tty(self, message: str) -> None:
        '''Writes to the opened pseudoterminal that communicates with with gdb.

        Parameters:
            message (str): The message to send.
        '''
        write(self.tty_fd, (message + '\n').encode('utf-8'))

    def stop_tty(self) -> None:
        '''Stops the pseudoterminal thread.'''
        self.is_stopped.set()
        try:
            write(self.tty_fd, '\n'.encode('utf-8'))
        except OSError:
            pass  # Ignore error if tty has been stopped already

    def is_multi_modifier_down(self) -> bool:
        '''Checks if shift or ctrl (cmd for mac os) are pressed'''
        is_multi_modifier_down: bool = dpg.is_key_down(dpg.mvKey_Shift)
        if self.is_mac_os:
            is_multi_modifier_down =\
                is_multi_modifier_down or dpg.is_key_down(dpg.mvKey_LWin) or dpg.is_key_down(dpg.mvKey_RWin)
        else:
            is_multi_modifier_down = is_multi_modifier_down or dpg.is_key_down(dpg.mvKey_Control)
        return is_multi_modifier_down
