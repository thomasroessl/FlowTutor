

from node import Node
from nodetype import NodeType


class Conditional(Node):

    @property
    def type(self):
        return NodeType.Conditional

    @property
    def width(self):
        return 150

    @property
    def height(self):
        return 100

    @property
    def raw_in_points(self):
        return [(75, 0)]

    @property
    def raw_out_points(self):
        return [(0, 50), (150, 50)]

    @property
    def color(self):
        return (255, 170, 170)

    @property
    def shape(self):
        return [
            (75, 0),
            (0, 50),
            (75, 100),
            (150, 50),
            (75, 0)
        ]
