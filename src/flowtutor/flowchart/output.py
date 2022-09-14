from flowtutor.flowchart.node import Node


class Output(Node):

    @property
    def shape_width(self):
        return 150

    @property
    def shape_height(self):
        return 75

    @property
    def raw_in_points(self):
        return [(75, 0)]

    @property
    def raw_out_points(self):
        return [(75, 75)]

    @property
    def color(self):
        return (147, 255, 149)

    @property
    def shape_points(self):
        return [
            (20, 0),
            (150, 0),
            (130, 75),
            (0, 75),
            (20, 0)
        ]

    @property
    def label(self):
        return self.__class__.__name__
