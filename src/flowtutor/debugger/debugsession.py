from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from dependency_injector.wiring import Provide, inject


if TYPE_CHECKING:
    from flowtutor.gui.debugger import Debugger
    from flowtutor.util_service import UtilService
    from flowtutor.flowchart.flowchart import Flowchart


class DebugSession(ABC):

    @inject
    def __init__(self, debugger: Debugger, utils_service: UtilService = Provide['utils_service']):
        self.debugger = debugger
        self.utils = utils_service

    @abstractmethod
    def run(self, flowchart: Flowchart) -> None:
        pass

    @abstractmethod
    def cont(self, flowchart: Flowchart) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def step(self, flowchart: Flowchart) -> None:
        pass

    @abstractmethod
    def next(self, flowchart: Flowchart) -> None:
        pass

    @abstractmethod
    def write(self, value: str) -> None:
        pass
