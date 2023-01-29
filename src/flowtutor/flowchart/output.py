from flowtutor.flowchart.node import Node


class Output(Node):

    def __init__(self):
        super().__init__()
        self._format_string = ''
        self._arguments = ''

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
        return (147, 255, 149) if self.is_initialized else (255, 0, 0)

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
    def arguments(self) -> str:
        return self._arguments

    @arguments.setter
    def arguments(self, arguments: str):
        self._arguments = arguments

    @property
    def format_string(self) -> str:
        return self._format_string

    @format_string.setter
    def format_string(self, format_string: str):
        self._format_string = format_string

    @property
    def label(self) -> str:
        if self.format_string and self.arguments:
            return f'Output:\n{self.format_string}: {self.arguments}'
        elif self.format_string:
            return f'Output:\n{self.format_string}'
        else:
            return self.__class__.__name__

    @property
    def is_initialized(self) -> bool:
        return len(self.format_string) > 0
