

from typing import Optional
import dearpygui.dearpygui as dpg

from flowtutor.flowchart.node import Node, FLOWCHART_TAG
from flowtutor.themes import theme_colors


class Conditional(Node):

    @property
    def width(self):
        return 150

    @property
    def height(self):
        return 100

    @property
    def raw_in_points(self):
        return [(75, 0)]

    @property
    def raw_out_points(self):
        return [(0, 50), (150, 50)]

    @property
    def color(self):
        return (255, 170, 170)

    @property
    def shape(self):
        return [
            (75, 0),
            (0, 50),
            (75, 100),
            (150, 50),
            (75, 0)
        ]

    def draw(self, mouse_pos: Optional[tuple[int, int]], is_selected=False):
        super().draw(mouse_pos, is_selected)
        pos_x, pos_y = self.pos
        tag = self.tag+"$"
        if dpg.does_item_exist(tag):
            return
        with dpg.draw_node(
                tag=tag,
                parent=FLOWCHART_TAG):
            text_color = theme_colors[(dpg.mvThemeCol_Text, 0)]

            text_false = "False"
            text_false_width, text_false_height = dpg.get_text_size(
                text_false)
            dpg.draw_text((pos_x - text_false_width - 5, pos_y + self.height/2 - text_false_height - 5),
                          text_false, color=text_color, size=18)

            text_true = "True"
            _, text_true_height = dpg.get_text_size(text_true)
            dpg.draw_text((pos_x + self.width + 5, pos_y + self.height/2 - text_true_height - 5),
                          text_true, color=text_color, size=18)

    def delete(self):
        super().delete()
        tag = self.tag+"$"
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)
