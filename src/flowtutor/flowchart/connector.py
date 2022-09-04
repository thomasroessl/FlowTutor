from flowtutor.flowchart.node import Node


class Connector(Node):

    @property
    def width(self):
        return 50

    @property
    def height(self):
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
    def shape(self):
        return [
            (25, 25)
        ]
