from typing import Optional, Tuple
import dearpygui.dearpygui as dpg

from flowtutor.flowchart.node import FLOWCHART_TAG, Node


class Declaration(Node):

    def __init__(self):
        super().__init__()
        self._var_name = ''
        self._var_type = 'Integer'

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
        return (255, 255, 170)

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
            return f'{self.var_type} {self.var_name}'
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

    def draw(self, mouse_pos: Optional[Tuple[int, int]], is_selected=False):
        super().draw(mouse_pos, is_selected)
        pos_x, pos_y = self.pos
        tag = self.tag+"$"
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

    def delete(self):
        super().delete()
        tag = self.tag+"$"
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)
