from node import Node
from nodetype import NodeType


class Assignment(Node):

    @property
    def type(self):
        return NodeType.Assignment
    
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
        return (255, 255, 170)

    @property
    def shape(self):
        return [
            (0, 0),
            (150, 0),
            (150, 75),
            (0, 75),
            (0, 0)
        ]
