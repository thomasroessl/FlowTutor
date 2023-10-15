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
    '''Handles interaction with GDB.

    GDB gets started as a subprocess and the GdbSession communicates via a TTY, if available.
    If TTY is not available on a system, e.g. Windows, the a seperate terminal window opens for communication with
    the program to debug.

    For easier communication with GDB, thre are several command line options set:
    - The GDB prompt is on a seperate line
    - The interpreter is set to machine interface (GDBMI)
    '''

    def __init__(self, debugger: Debugger):
        super().__init__(debugger)
        self._gdb_process: Optional[Popen[str]] = None

        # Builds an argument list for GDB with the executable file that comes from GCC.
        try:
            self.gdb_args = [self.utils_service.get_gdb_exe(),
                             '-q',
                             '-x',
                             self.utils_service.get_gdb_commands_path(),
                             '--interpreter=mi',
                             self.utils_service.get_exe_path()]
        except FileNotFoundError as error:
            self.debugger.log_error(str(error))
            return

        # Runs GDB with the argument list from above.
        print('GDB ARGS', self.gdb_args, file=stderr)
        self._gdb_process = Popen(self.gdb_args,
                                  stdout=PIPE,
                                  stderr=STDOUT,
                                  stdin=PIPE,
                                  text=True,
                                  bufsize=1)

        if not self.process or not self.process.stdout or not self.process.stdin:
            return

        self.break_point_path = self.utils_service.get_break_points_path()
        '''The path to the break point definiton file.'''

        # Reads all lines from the output until it encounters the GDB prompt.
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
        '''The subprocess running GDB.'''
        return self._gdb_process

    def run(self, flowchart: Flowchart) -> None:
        # Before continuing, refresh the break points, in case the user has altered them.
        self.refresh_break_points(flowchart)
        self.execute('-exec-run\n', flowchart)

    def cont(self, flowchart: Flowchart) -> None:
        # Before continuing, refresh the break points, in case the user has altered them.
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

    def write(self, value: str) -> None:
        self.utils_service.write_tty(value)

    def execute(self, command: str, flowchart: Flowchart) -> None:
        '''Sends a command to GDB in the subprocess.

        Parameters:
            command (str): The command to execute.
            flowchart (Flowchart): The instance of the debugged flowchart.
        '''
        if not self.process:
            return

        # The commands get sent from a seperate thread.
        def t(self: GdbSession) -> None:
            if not self.process or not self.process.stdin or not self.process.stdout:
                return
            print('START EXECUTE:', command, file=stderr)
            self.process.stdin.write(f'{command}\n')

            # Reads all lines from the output of the subprocesses stdout.
            for line in self.process.stdout:

                # Detects if GDB is not code-signed on the executing machine.
                # The debugger is quit, if this is the case.
                if line.startswith('^error,msg="Unable to find Mach'):
                    self.process.kill()
                    self._gdb_process = None
                    self.debugger.log_error('GDB is not code-signed on this machine.')

                # Parses the output line into a dictionary.
                record = gdbmiparser.parse_response(line)

                print(f'EXECUTE {command}', record, file=stderr)
                if record['message'] == 'stopped':
                    reason = record['payload']['reason']
                    if reason == 'exited-normally':
                        # Emit a signal that the program is finished if it exited normally.
                        signal('program-finished').send(self)
                    elif reason == 'breakpoint-hit' or reason == 'end-stepping-range':
                        frame = record['payload']['frame']
                        if frame['func'] == '??':
                            # On the end of the program, the debugger hits a frame that gets skipped, so the user
                            # doesn't have to step through it manually.
                            self.cont(flowchart)
                        else:
                            self.get_variable_assignments()
                            # Emit a signal if a break point is hit or the user is stepping to the current line.
                            signal('hit-line').send(self, line=int(frame['line']))
                    elif reason == 'signal-received':
                        meaning = record['payload']['signal-meaning']
                        # Emit a signal that the program is finished, if an error occurs.
                        signal('program-error').send(self, error=meaning)
                        signal('program-finished').send(self)
                    break
                # Emit a signal that the program is finished, if an error occurs.
                elif record['message'] == 'error':
                    signal('program-finished').send(self)

            print('END EXECUTE:', command, file=stderr)
        Thread(target=t, args=[self]).start()

    def refresh_break_points(self, flowchart: Flowchart) -> None:
        if not self.process or not self.process.stdin:
            return
        # Tries to remove an existing break point definiton file.
        try:
            remove(self.break_point_path)
        except FileNotFoundError:
            pass
        # Make the contents of the break point definiton file.
        break_point_definitions = '\n'.join(
            map(lambda line: f'break flowtutor.c:{line}', flowchart.break_points))

        # Write the break point definitons to a file.
        with open(self.break_point_path, 'w') as file:
            file.write(break_point_definitions)

        # Remove exising break points in the debugger execution instance.
        self.process.stdin.write('-break-delete\n')

        # Load the new break point definition file.
        self.process.stdin.write(f'source {self.utils_service.get_break_points_path()}\n')

    def get_variable_assignments(self) -> None:
        '''Communicates with the GDB subprocess to get loval variable assignments of the debugged program.

        Emits the varaibles through a signal.
        '''
        if not self.process or not self.process.stdout or not self.process.stdin:
            return
        variables: dict[str, str] = {}

        # A list of variables the need another call to GDB to identify, e.g. pointers.
        unknown_value_vars: list[str] = []
        self.process.stdin.write('-stack-list-locals --simple-values\n')
        for line in self.process.stdout:
            # Parses the output line into a dictionary.
            record = gdbmiparser.parse_response(line)

            print('VARIABLE_ASSIGNMENTS', record, file=stderr)
            if record['message'] == 'stopped':
                # Stops reading the output if it gets the "stopped" message
                break
            elif record['type'] == 'result' and record['message'] == 'done':
                if record['payload']:
                    result_locals = record['payload']['locals']
                    if result_locals:
                        for var in result_locals:
                            if cast(str, var['type']).endswith('*'):
                                # Values of pointers are unknown, since they are only raw memory adresses.
                                unknown_value_vars.append(f'*{var["name"]}')
                            elif 'value' in var:
                                # Value types can be read directly.
                                variables[var['name']] = str(var['value'])
                            else:
                                unknown_value_vars.append(var['name'])
                        print('VARIABLE_ASSIGNMENTS', variables, file=stderr)
                    break

        for var_name in unknown_value_vars:
            # For the unknown variables, another call to GDB is made.
            self.process.stdin.write(f'print {var_name}\n')
            for line in self.process.stdout:
                record = gdbmiparser.parse_response(line)
                print(f'PRINT_VARIABLE {var_name}', record, file=stderr)
                if record['message'] == 'stopped':
                    # Stops reading the output if it gets the "stopped" message
                    break
                elif record['type'] == 'result' and record['message'] == 'done':
                    break
                elif record['type'] == 'console':
                    payload = str(record['payload'])
                    # Use regex, to get the value of the variable from the console output.
                    # Example: x = 15
                    match = search(r'^\$1 = (.*)', payload.strip())
                    if match:
                        variables[var_name] = str(match.group(1))

        # Emits a signal with the dictionary of variable assignments.
        signal('variables').send(self, variables=variables)
