from __future__ import annotations
from shapely.geometry import Point

from flowtutor.flowchart.node import Node


class Connector(Node):
    '''A connecting node for connecting the branches after a decision.'''

    def __init__(self) -> None:
        super().__init__()
        self._shape_data = [list(Point(25, 25).buffer(25).exterior.coords)]

    @property
    def shape_width(self) -> int:
        return 50

    @property
    def shape_height(self) -> int:
        return 50

    @property
    def raw_in_points(self) -> list[tuple[float, float]]:
        return [(25, 0)]

    @property
    def raw_out_points(self) -> list[tuple[float, float]]:
        return [(25, 50)]

    @property
    def color(self) -> tuple[int, int, int]:
        return (255, 170, 170)

    @property
    def label(self) -> str:
        return ''

    @property
    def is_initialized(self) -> bool:
        return True
