from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

from flowtutor.flowchart.node import Node


class Sidebar(ABC):

    @abstractmethod
    def hide(self) -> None:
        pass

    @abstractmethod
    def show(self, node: Optional[Node]) -> None:
        pass
