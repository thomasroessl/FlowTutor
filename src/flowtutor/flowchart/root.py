from flowtutor.flowchart.node import Node


class Root(Node):

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
        return (200, 170, 255)

    @property
    def shape_points(self):
        return [
            (0, 37.5),
            (1, 30),
            (3, 23),
            (6, 17),
            (11, 11),
            (17, 6),
            (23, 3),
            (30, 1),
            (37.5, 0),
            (112.5, 0),
            (120, 1),
            (127, 3),
            (133, 6),
            (139, 11),
            (144, 17),
            (147, 23),
            (149, 30),
            (150, 37.5),
            (149, 45),
            (147, 52),
            (144, 58),
            (139, 64),
            (133, 69),
            (127, 72),
            (120, 74),
            (112.5, 75),
            (37.5, 75),
            (30, 74),
            (23, 72),
            (17, 69),
            (11, 64),
            (6, 58),
            (3, 52),
            (1, 45),
            (0, 37.5)
        ]

    @property
    def label(self):
        return 'Main'
