from flowtutor.flowchart.node import Node


class Assignment(Node):

    def __init__(self):
        super().__init__()
        self._var_name = ''
        self._var_offset = ''
        self._var_value = ''

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
        return (255, 255, 170) if self.is_initialized else (255, 0, 0)

    @property
    def shape_points(self):
        return [
            (0, 0),
            (150, 0),
            (150, 75),
            (0, 75),
            (0, 0)
        ]

    @property
    def label(self) -> str:
        if self.var_name and self.var_value:
            return f'{self.var_name}{f"[{self.var_offset}]" if len(self.var_offset) > 0 else ""} = {self.var_value}'
        else:
            return self.__class__.__name__

    @property
    def var_name(self) -> str:
        return self._var_name

    @var_name.setter
    def var_name(self, var_name: str):
        self._var_name = var_name

    @property
    def var_offset(self) -> str:
        return self._var_offset

    @var_offset.setter
    def var_offset(self, var_offset: str):
        self._var_offset = var_offset

    @property
    def var_value(self) -> str:
        return self._var_value

    @var_value.setter
    def var_value(self, var_value: str):
        self._var_value = var_value

    @property
    def is_initialized(self) -> bool:
        return len(self.var_name) > 0 and len(self.var_value) > 0
