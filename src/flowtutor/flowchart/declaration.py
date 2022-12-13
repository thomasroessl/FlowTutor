from typing import Optional, Tuple
import dearpygui.dearpygui as dpg

from flowtutor.flowchart.node import FLOWCHART_TAG, Node


class Declaration(Node):

    def __init__(self):
        super().__init__()
        self._var_name = ''
        self._var_type = 'int'
        self._var_value = ''
        self._array_size = ''
        self._is_array = False
        self._is_pointer = False

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
        if self.var_name:
            return ''.join([f'{self.var_type} ',
                            '*' if self.is_pointer else '',
                            self.var_name,
                            f'[{self.array_size}]' if self.is_array else '',
                            f' = {self.var_value}' if len(self.var_value) > 0 else '',
                            ';'])
        else:
            return self.__class__.__name__

    @property
    def var_name(self) -> str:
        return self._var_name

    @var_name.setter
    def var_name(self, var_name: str):
        self._var_name = var_name

    @property
    def var_type(self) -> str:
        return self._var_type

    @var_type.setter
    def var_type(self, var_type: str):
        self._var_type = var_type

    @property
    def var_value(self) -> str:
        return self._var_value

    @var_value.setter
    def var_value(self, var_value: str):
        self._var_value = var_value

    @property
    def is_array(self) -> bool:
        return self._is_array

    @is_array.setter
    def is_array(self, is_array: bool):
        self._is_array = is_array
        if is_array:
            self.var_value = ''
        else:
            self.array_size = ''

    @property
    def array_size(self) -> str:
        return self._array_size

    @array_size.setter
    def array_size(self, array_size: str):
        self._array_size = array_size

    @property
    def is_pointer(self) -> bool:
        return self._is_pointer

    @is_pointer.setter
    def is_pointer(self, is_pointer: bool):
        self._is_pointer = is_pointer

    def draw(self, mouse_pos: Optional[Tuple[int, int]], is_selected=False):  # pragma: no cover
        super().draw(mouse_pos, is_selected)
        pos_x, pos_y = self.pos
        tag = self.tag+'$'
        if dpg.does_item_exist(tag):
            return
        # Draw extra lines for the declaration node
        with dpg.draw_node(
                tag=tag,
                parent=FLOWCHART_TAG):
            text_color = (0, 0, 0)

            dpg.draw_line(
                (pos_x + 10 + self.get_left_x(), pos_y),
                (pos_x + 10 + self.get_left_x(), pos_y + self.shape_height),
                color=text_color,
                thickness=1)

            dpg.draw_line(
                (pos_x + self.get_left_x(), pos_y + 10),
                (pos_x + self.get_right_x(), pos_y + 10),
                color=text_color,
                thickness=1)

    def delete(self):  # pragma: no cover
        super().delete()
        tag = self.tag+'$'
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)

    @property
    def is_initialized(self) -> bool:
        is_initialized = True
        if self.is_array:
            is_initialized = len(self.array_size) > 0
        return is_initialized and len(self.var_name) > 0
