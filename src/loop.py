import dearpygui.dearpygui as dpg

from node import Node
from nodetype import NodeType


class Loop(Node):

    @property
    def type(self):
        return NodeType.Loop

    @property
    def width(self):
        return 150

    @property
    def height(self):
        return 75

    @property
    def raw_in_points(self):
        return [(75, 0), (110, 75)]

    @property
    def raw_out_points(self):
        return [(75, 75), (150, 37.5)]

    @property
    def color(self):
        return (255, 208, 147)

    @property
    def shape(self):
        return [
            (0, 37.5),
            (20, 75),
            (130, 75),
            (150, 37.5),
            (130, 0),
            (20, 0),
            (0, 37.5)
        ]

    def draw(self, parent: str, mouse_pos: tuple, connections, is_selected=False):
        super().draw(parent, mouse_pos, is_selected)
        pos_x, pos_y = self.pos
        tag = self.tag+"$"
        if dpg.does_item_exist(tag):
            return
        with dpg.draw_node(
                tag=tag,
                parent=parent):

            text_false = "False"
            text_false_width, text_false_height = dpg.get_text_size(
                text_false)
            dpg.draw_text((pos_x + self.width / 2 - text_false_width - 10, pos_y + self.height + 5),
                          text_false, color=self.color, size=18)

            text_true = "True"
            _, text_true_height = dpg.get_text_size(text_true)
            dpg.draw_text((pos_x + self.width + 5, pos_y + self.height/2 - text_true_height - 5),
                          text_true, color=self.color, size=18)

    def delete(self):
        super().delete()
        tag = self.tag+"$"
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)
