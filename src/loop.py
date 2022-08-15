

from node import Node
from nodetype import NodeType


class Loop(Node):

    @property
    def type(self):
        return NodeType.Loop

    @property
    def width(self):
        return 150

    @property
    def height(self):
        return 75

    @property
    def raw_in_points(self):
        return [(75, 0)]

    @property
    def raw_out_points(self):
        return [(75, 75)]

    @property
    def color(self):
        return (255, 208, 147)

    @property
    def shape(self):
        return [
            (0, 37.5),
            (20, 75),
            (130, 75),
            (150, 37.5),
            (130, 0),
            (20, 0),
            (0, 37.5)
        ]
