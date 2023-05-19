from __future__ import annotations
import math
from typing import TYPE_CHECKING, Any, Optional
import dearpygui.dearpygui as dpg

from flowtutor.flowchart.node import FLOWCHART_TAG, Node

if TYPE_CHECKING:
    from flowtutor.flowchart.flowchart import Flowchart


class Declarations(Node):

    def __init__(self) -> None:
        super().__init__()
        self._declarations = [
            self.new_declaration()
        ]

    @property
    def shape_width(self) -> int:
        return 150

    @property
    def shape_height(self) -> int:
        _, height = dpg.get_text_size(self.label)
        return 57 + int(math.floor(height))

    @property
    def raw_in_points(self) -> list[tuple[float, float]]:
        return [(75, 0)]

    @property
    def raw_out_points(self) -> list[tuple[float, float]]:
        return [(75, self.shape_height)]

    @property
    def color(self) -> tuple[int, int, int]:
        return (255, 255, 170) if self.is_initialized else (255, 0, 0)

    @property
    def shape_points(self) -> list[tuple[float, float]]:
        return [
            (0, 0),
            (150, 0),
            (150, self.shape_height),
            (0, self.shape_height),
            (0, 0)
        ]

    @property
    def declarations(self) -> list[dict[str, Any]]:
        return self._declarations

    @declarations.setter
    def declarations(self, declarations: list[dict[str, Any]]) -> None:
        self._declarations = declarations

    @property
    def label(self) -> str:
        if all(map(lambda d: d['var_name'], self.declarations)):
            return '\n'.join(map(lambda d: ''.join([
                'static ' if d['is_static'] else '',
                d['var_type'],
                ' ',
                '*' if d['is_pointer'] else '',
                d['var_name'],
                f'[{d["array_size"]}]' if d['is_array'] else '',
                f' = {d["var_value"]}' if len(d['var_value']) > 0 else '',
                ';']), self.declarations))
        else:
            return self.__class__.__name__

    def draw(self,
             flowchart: Flowchart,
             mouse_pos: Optional[tuple[int, int]],
             is_selected: bool = False) -> None:  # pragma: no cover
        super().draw(flowchart, mouse_pos, is_selected)
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

    def delete(self) -> None:  # pragma: no cover
        super().delete()
        tag = self.tag+'$'
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)

    @property
    def is_initialized(self) -> bool:
        for d in self.declarations:
            if d['is_array'] and len(d['array_size']) <= 0:
                return self.is_comment
            elif len(d['var_name']) <= 0:
                return self.is_comment
        return True

    def new_declaration(self) -> dict[str, Any]:
        return {
            'var_name': '',
            'var_type': 'int',
            'var_value': '',
            'array_size': '',
            'is_array': False,
            'is_pointer':  False,
            'is_static':  False
        }

    def add_declaration(self) -> None:
        self.declarations.append(self.new_declaration())

    def delete_declaration(self, index: int) -> None:
        del self.declarations[index]
