from shapely.geometry import Point

from flowtutor.flowchart.node import Node


class Connector(Node):

    _shape_points = list(Point(25, 25).buffer(25).exterior.coords)

    @property
    def shape_width(self):
        return 50

    @property
    def shape_height(self):
        return 50

    @property
    def raw_in_points(self):
        return [(25, 0)]

    @property
    def raw_out_points(self):
        return [(25, 50)]

    @property
    def color(self):
        return (255, 170, 170)

    @property
    def shape_points(self):
        return self._shape_points

    @property
    def label(self):
        return ''
