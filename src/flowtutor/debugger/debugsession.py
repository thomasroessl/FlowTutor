from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from dependency_injector.wiring import Provide, inject

if TYPE_CHECKING:
    from flowtutor.gui.debugger import Debugger
    from flowtutor.util_service import UtilService


class DebugSession(ABC):

    @inject
    def __init__(self, debugger: Debugger, utils_service: UtilService = Provide['utils_service']):
        self.debugger = debugger
        self.utils = utils_service

    @abstractmethod
    def run(self) -> None:
        pass

    @abstractmethod
    def cont(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def step(self) -> None:
        pass

    @abstractmethod
    def next(self) -> None:
        pass

    @abstractmethod
    def refresh_break_points(self) -> None:
        pass

    @abstractmethod
    def get_variable_assignments(self) -> None:
        pass
