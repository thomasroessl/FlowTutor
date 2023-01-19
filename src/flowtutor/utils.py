import sys
import platform
import pathlib

from shutil import which, rmtree
from tempfile import mkdtemp
from os import path

root = pathlib.Path(sys.modules['__main__'].__file__ or '').parent.resolve()

temp_dir = mkdtemp(None, 'flowtutor-')


def cleanup_temp():
    '''Deletes the temporary working directory.'''
    rmtree(temp_dir)


def get_root_dir():
    '''Gets the root directory of the application.'''
    return root


def get_gcc_exe():
    '''Gets the path to the installed gcc, or the packaged version of mingw on Windows.'''
    if (exe := which('gcc-12')) is not None:
        return exe
    elif (exe := which('gcc')) is not None:
        return exe
    elif platform.system() == 'Windows':
        return path.join(root, 'mingw64', 'bin', 'gcc.exe')
    else:
        raise FileNotFoundError('gcc could not be found on the system!')


def get_gdb_exe():
    '''Gets the path to the installed gdb, or the packaged version of mingw on Windows.'''
    if (exe := which('gdb')) is not None:
        return exe
    elif platform.system() == 'Windows':
        path.join(root, 'mingw', 'bin', 'gdb.exe')
    else:
        raise FileNotFoundError('gdb could not be found on the system!')


def get_exe_path():
    '''Gets the path to the executable compiled by flowtutor (through gcc).'''
    return path.join(temp_dir, 'flowtutor.exe')


def get_gdb_commands_path():
    '''Creates and gets the path to the command file used for starting gdb.'''
    gdb_commands_path = path.join(temp_dir, 'gdb_commands')
    gdb_commands = 'set prompt (gdb)\\n'
    # The following command is needed for gdb to run on MacOS with System Integrity Protection
    if platform.system() == 'Darwin':
        gdb_commands += '\nset startup-with-shell off'
    gdb_commands += f'\nsource {get_break_points_path()}'
    with open(gdb_commands_path, 'w') as gdb_commands_file:
        gdb_commands_file.write(gdb_commands)
    return gdb_commands_path


def get_c_source_path():
    '''Gets the path to the generated C-source code of the flowchart.'''
    return path.join(temp_dir, 'flowtutor.c')


def get_break_points_path():
    '''Gets the path to the break-point file for gdb.'''
    return path.join(temp_dir, 'flowtutor_break_points')
