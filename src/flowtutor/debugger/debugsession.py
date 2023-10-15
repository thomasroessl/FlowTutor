from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from dependency_injector.wiring import Provide, inject


if TYPE_CHECKING:
    from flowtutor.gui.debugger import Debugger
    from flowtutor.util_service import UtilService
    from flowtutor.flowchart.flowchart import Flowchart


class DebugSession(ABC):
    '''A generic interface for debugging FlowtutorPrograms.

    The debugger GUI uses an instance of a DebugSession for user interaction.
    '''

    @inject
    def __init__(self, debugger: Debugger, utils_service: UtilService = Provide['utils_service']):
        self.debugger = debugger
        '''A reference to the GUI element.'''
        self.utils_service = utils_service

    @abstractmethod
    def run(self, flowchart: Flowchart) -> None:
        '''Run the program.

        Parameters:
            flowchart (Flowchart): The instance of the debugged flowchart.
        '''
        pass

    @abstractmethod
    def cont(self, flowchart: Flowchart) -> None:
        '''Continue execution of the program until the end or the next break point.

        Parameters:
            flowchart (Flowchart): The instance of the debugged flowchart.
        '''
        pass

    @abstractmethod
    def stop(self) -> None:
        '''Stop execution of the program.'''
        pass

    @abstractmethod
    def step(self, flowchart: Flowchart) -> None:
        '''Excecute a single step of the program, stepping into functions.

        Parameters:
            flowchart (Flowchart): The instance of the debugged flowchart.
        '''
        pass

    @abstractmethod
    def next(self, flowchart: Flowchart) -> None:
        '''Excecute a single step of the program, stepping over functions.

        Parameters:
            flowchart (Flowchart): The instance of the debugged flowchart.
        '''
        pass

    @abstractmethod
    def write(self, value: str) -> None:
        '''Writes user input into the debugger.

        Parameters:
            value (str): The value to send to the debugger.
        '''
        pass

    @abstractmethod
    def refresh_break_points(self, flowchart: Flowchart) -> None:
        '''Refreshes the breakpoints set by the user inside the debugger instance.

        This method has to be called, when the user makes changes to the break points.

        Parameters:
            flowchart (Flowchart): The instance of the debugged flowchart.
        '''
        pass
