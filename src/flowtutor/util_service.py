from pathlib import Path
from platform import system
from select import select
from sys import modules, stdin
from threading import Event, Thread
from typing import Optional
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
        '''The root directory of the application.'''
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
        self.theme_colors: dict[int, tuple[int, int, int, int]] = {}
        '''The colors of the current theme.'''
        self._theme_light: Optional[int] = None
        self._theme_dark: Optional[int] = None

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

    def __set_theme_color(self, target: int, color: tuple[int, int, int, int]) -> None:
        dpg.add_theme_color(target, color)
        self.theme_colors[target] = color

    def get_theme_dark(self) -> int:
        '''Gets the dark dpg theme.'''
        if self._theme_dark is None:
            self._theme_dark = self.__create_theme_dark()
        return self._theme_dark

    def get_theme_light(self) -> int:
        '''Gets the light dpg theme.'''
        if self._theme_light is None:
            self._theme_light = self.__create_theme_light()
        return self._theme_light

    def __create_theme_dark(self) -> int:
        '''Creates the dark dpg theme.'''
        with dpg.theme() as theme_id:
            with dpg.theme_component(dpg.mvAll):
                self.__set_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 255))
                self.__set_theme_color(dpg.mvThemeCol_TextDisabled, (128, 128, 128, 255))
                self.__set_theme_color(dpg.mvThemeCol_WindowBg, (15, 15, 15, 240))
                self.__set_theme_color(dpg.mvThemeCol_ChildBg, (0, 0, 0, 0))
                self.__set_theme_color(dpg.mvThemeCol_PopupBg, (20, 20, 20, 240))
                self.__set_theme_color(dpg.mvThemeCol_Border, (110, 110, 128, 128))
                self.__set_theme_color(dpg.mvThemeCol_BorderShadow, (0, 0, 0, 0))
                self.__set_theme_color(dpg.mvThemeCol_FrameBg, (41, 74, 122, 138))
                self.__set_theme_color(dpg.mvThemeCol_FrameBgHovered, (66, 150, 250, 102))
                self.__set_theme_color(dpg.mvThemeCol_FrameBgActive, (66, 150, 250, 171))
                self.__set_theme_color(dpg.mvThemeCol_TitleBg, (10, 10, 10, 255))
                self.__set_theme_color(dpg.mvThemeCol_TitleBgActive, (41, 74, 122, 255))
                self.__set_theme_color(dpg.mvThemeCol_TitleBgCollapsed, (0, 0, 0, 130))
                self.__set_theme_color(dpg.mvThemeCol_MenuBarBg, (36, 36, 36, 255))
                self.__set_theme_color(dpg.mvThemeCol_ScrollbarBg, (5, 5, 5, 135))
                self.__set_theme_color(dpg.mvThemeCol_ScrollbarGrab, (79, 79, 79, 255))
                self.__set_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, (105, 105, 105, 255))
                self.__set_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, (130, 130, 130, 255))
                self.__set_theme_color(dpg.mvThemeCol_CheckMark, (66, 150, 250, 255))
                self.__set_theme_color(dpg.mvThemeCol_SliderGrab, (61, 133, 224, 255))
                self.__set_theme_color(dpg.mvThemeCol_SliderGrabActive, (66, 150, 250, 255))
                self.__set_theme_color(dpg.mvThemeCol_Button, (66, 150, 250, 102))
                self.__set_theme_color(dpg.mvThemeCol_ButtonHovered, (66, 150, 250, 255))
                self.__set_theme_color(dpg.mvThemeCol_ButtonActive, (15, 135, 250, 255))
                self.__set_theme_color(dpg.mvThemeCol_Header, (66, 150, 250, 79))
                self.__set_theme_color(dpg.mvThemeCol_HeaderHovered, (66, 150, 250, 204))
                self.__set_theme_color(dpg.mvThemeCol_HeaderActive, (66, 150, 250, 255))
                self.__set_theme_color(dpg.mvThemeCol_Separator, (110, 110, 128, 128))
                self.__set_theme_color(dpg.mvThemeCol_SeparatorHovered, (26, 102, 191, 199))
                self.__set_theme_color(dpg.mvThemeCol_SeparatorActive, (26, 102, 191, 255))
                self.__set_theme_color(dpg.mvThemeCol_ResizeGrip, (66, 150, 250, 51))
                self.__set_theme_color(dpg.mvThemeCol_ResizeGripHovered, (66, 150, 250, 171))
                self.__set_theme_color(dpg.mvThemeCol_ResizeGripActive, (66, 150, 250, 242))
                self.__set_theme_color(dpg.mvThemeCol_Tab, (46, 89, 148, 219))
                self.__set_theme_color(dpg.mvThemeCol_TabHovered, (66, 150, 250, 204))
                self.__set_theme_color(dpg.mvThemeCol_TabActive, (51, 105, 173, 255))
                self.__set_theme_color(dpg.mvThemeCol_TabUnfocused, (18, 26, 38, 247))
                self.__set_theme_color(dpg.mvThemeCol_TabUnfocusedActive, (36, 66, 107, 255))
                self.__set_theme_color(dpg.mvThemeCol_DockingPreview, (66, 150, 250, 179))
                self.__set_theme_color(dpg.mvThemeCol_DockingEmptyBg, (51, 51, 51, 255))
                self.__set_theme_color(dpg.mvThemeCol_PlotLines, (156, 156, 156, 255))
                self.__set_theme_color(dpg.mvThemeCol_PlotLinesHovered, (255, 110, 89, 255))
                self.__set_theme_color(dpg.mvThemeCol_PlotHistogram, (230, 179, 0, 255))
                self.__set_theme_color(dpg.mvThemeCol_PlotHistogramHovered, (255, 153, 0, 255))
                self.__set_theme_color(dpg.mvThemeCol_TableHeaderBg, (48, 48, 51, 255))
                self.__set_theme_color(dpg.mvThemeCol_TableBorderStrong, (79, 79, 89, 255))
                self.__set_theme_color(dpg.mvThemeCol_TableBorderLight, (59, 59, 64, 255))
                self.__set_theme_color(dpg.mvThemeCol_TableRowBg, (0, 0, 0, 0))
                self.__set_theme_color(dpg.mvThemeCol_TableRowBgAlt, (255, 255, 255, 15))
                self.__set_theme_color(dpg.mvThemeCol_TextSelectedBg, (66, 150, 250, 89))
                self.__set_theme_color(dpg.mvThemeCol_DragDropTarget, (255, 255, 0, 230))
                self.__set_theme_color(dpg.mvThemeCol_NavHighlight, (66, 150, 250, 255))
                self.__set_theme_color(dpg.mvThemeCol_NavWindowingHighlight, (255, 255, 255, 179))
                self.__set_theme_color(dpg.mvThemeCol_NavWindowingDimBg, (204, 204, 204, 51))
                self.__set_theme_color(dpg.mvThemeCol_ModalWindowDimBg, (204, 204, 204, 89))

            with dpg.theme_component(dpg.mvImageButton, enabled_state=False):
                self.__set_theme_color(dpg.mvThemeCol_Button, (50, 50, 50, 255))
                self.__set_theme_color(dpg.mvThemeCol_ButtonHovered, (50, 50, 50, 255))
                self.__set_theme_color(dpg.mvThemeCol_ButtonActive, (50, 50, 50, 255))

            with dpg.theme_component(dpg.mvButton, enabled_state=False):
                self.__set_theme_color(dpg.mvThemeCol_Button, (50, 50, 50, 255))
                self.__set_theme_color(dpg.mvThemeCol_ButtonHovered, (50, 50, 50, 255))
                self.__set_theme_color(dpg.mvThemeCol_ButtonActive, (50, 50, 50, 255))
        return int(theme_id)

    def __create_theme_light(self) -> int:
        '''Creates the light dpg theme.'''
        with dpg.theme() as theme_id:
            with dpg.theme_component(dpg.mvAll):
                self.__set_theme_color(dpg.mvThemeCol_Text, (0, 0, 0, 255))
                self.__set_theme_color(dpg.mvThemeCol_TextDisabled, (153, 153, 153, 255))
                self.__set_theme_color(dpg.mvThemeCol_WindowBg, (255, 255, 255, 255))
                self.__set_theme_color(dpg.mvThemeCol_ChildBg, (0, 0, 0, 0))
                self.__set_theme_color(dpg.mvThemeCol_PopupBg, (255, 255, 255, 250))
                self.__set_theme_color(dpg.mvThemeCol_Border, (0, 0, 0, 77))
                self.__set_theme_color(dpg.mvThemeCol_BorderShadow, (0, 0, 0, 0))
                self.__set_theme_color(dpg.mvThemeCol_FrameBg, (230, 230, 230, 255))
                self.__set_theme_color(dpg.mvThemeCol_FrameBgHovered, (66, 150, 250, 102))
                self.__set_theme_color(dpg.mvThemeCol_FrameBgActive, (66, 150, 250, 171))
                self.__set_theme_color(dpg.mvThemeCol_TitleBg, (245, 245, 245, 255))
                self.__set_theme_color(dpg.mvThemeCol_TitleBgActive, (209, 209, 209, 255))
                self.__set_theme_color(dpg.mvThemeCol_TitleBgCollapsed, (255, 255, 255, 130))
                self.__set_theme_color(dpg.mvThemeCol_MenuBarBg, (219, 219, 219, 255))
                self.__set_theme_color(dpg.mvThemeCol_ScrollbarBg, (250, 250, 250, 135))
                self.__set_theme_color(dpg.mvThemeCol_ScrollbarGrab, (176, 176, 176, 204))
                self.__set_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, (125, 125, 125, 204))
                self.__set_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, (125, 125, 125, 255))
                self.__set_theme_color(dpg.mvThemeCol_CheckMark, (66, 150, 250, 255))
                self.__set_theme_color(dpg.mvThemeCol_SliderGrab, (66, 150, 250, 199))
                self.__set_theme_color(dpg.mvThemeCol_SliderGrabActive, (117, 138, 204, 153))
                self.__set_theme_color(dpg.mvThemeCol_Button, (66, 150, 250, 102))
                self.__set_theme_color(dpg.mvThemeCol_ButtonHovered, (66, 150, 250, 255))
                self.__set_theme_color(dpg.mvThemeCol_ButtonActive, (15, 135, 250, 255))
                self.__set_theme_color(dpg.mvThemeCol_Header, (66, 150, 250, 79))
                self.__set_theme_color(dpg.mvThemeCol_HeaderHovered, (66, 150, 250, 204))
                self.__set_theme_color(dpg.mvThemeCol_HeaderActive, (66, 150, 250, 255))
                self.__set_theme_color(dpg.mvThemeCol_Separator, (99, 99, 99, 158))
                self.__set_theme_color(dpg.mvThemeCol_SeparatorHovered, (36, 112, 204, 199))
                self.__set_theme_color(dpg.mvThemeCol_SeparatorActive, (36, 112, 204, 255))
                self.__set_theme_color(dpg.mvThemeCol_ResizeGrip, (89, 89, 89, 43))
                self.__set_theme_color(dpg.mvThemeCol_ResizeGripHovered, (66, 150, 250, 171))
                self.__set_theme_color(dpg.mvThemeCol_ResizeGripActive, (66, 150, 250, 242))
                self.__set_theme_color(dpg.mvThemeCol_Tab, (194, 204, 214, 237))
                self.__set_theme_color(dpg.mvThemeCol_TabHovered, (66, 150, 250, 204))
                self.__set_theme_color(dpg.mvThemeCol_TabActive, (153, 186, 224, 255))
                self.__set_theme_color(dpg.mvThemeCol_TabUnfocused, (235, 237, 240, 252))
                self.__set_theme_color(dpg.mvThemeCol_TabUnfocusedActive, (189, 209, 232, 255))
                self.__set_theme_color(dpg.mvThemeCol_DockingPreview, (66, 150, 250, 56))
                self.__set_theme_color(dpg.mvThemeCol_DockingEmptyBg, (51, 51, 51, 255))
                self.__set_theme_color(dpg.mvThemeCol_PlotLines, (99, 99, 99, 255))
                self.__set_theme_color(dpg.mvThemeCol_PlotLinesHovered, (255, 110, 89, 255))
                self.__set_theme_color(dpg.mvThemeCol_PlotHistogram, (230, 179, 0, 255))
                self.__set_theme_color(dpg.mvThemeCol_PlotHistogramHovered, (255, 114, 0, 255))
                self.__set_theme_color(dpg.mvThemeCol_TableHeaderBg, (199, 222, 250, 255))
                self.__set_theme_color(dpg.mvThemeCol_TableBorderStrong, (145, 145, 163, 255))
                self.__set_theme_color(dpg.mvThemeCol_TableBorderLight, (173, 173, 189, 255))
                self.__set_theme_color(dpg.mvThemeCol_TableRowBg, (0, 0, 0, 0))
                self.__set_theme_color(dpg.mvThemeCol_TableRowBgAlt, (77, 77, 77, 23))
                self.__set_theme_color(dpg.mvThemeCol_TextSelectedBg, (66, 150, 250, 89))
                self.__set_theme_color(dpg.mvThemeCol_DragDropTarget, (66, 150, 250, 242))
                self.__set_theme_color(dpg.mvThemeCol_NavHighlight, (66, 150, 250, 204))
                self.__set_theme_color(dpg.mvThemeCol_NavWindowingHighlight, (179, 179, 179, 179))
                self.__set_theme_color(dpg.mvThemeCol_NavWindowingDimBg, (51, 51, 51, 51))
                self.__set_theme_color(dpg.mvThemeCol_ModalWindowDimBg, (51, 51, 51, 89))

            with dpg.theme_component(dpg.mvImageButton, enabled_state=False):
                self.__set_theme_color(dpg.mvThemeCol_Button, (220, 220, 220, 255))
                self.__set_theme_color(dpg.mvThemeCol_ButtonHovered, (220, 220, 220, 255))
                self.__set_theme_color(dpg.mvThemeCol_ButtonActive, (220, 220, 220, 255))

            with dpg.theme_component(dpg.mvButton, enabled_state=False):
                self.__set_theme_color(dpg.mvThemeCol_Button, (220, 220, 220, 255))
                self.__set_theme_color(dpg.mvThemeCol_ButtonHovered, (220, 220, 220, 255))
                self.__set_theme_color(dpg.mvThemeCol_ButtonActive, (220, 220, 220, 255))
        return int(theme_id)
