from typing import Optional
import dearpygui.dearpygui as dpg
from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.connector import Connector
from flowtutor.flowchart.loop import Loop
from flowtutor.flowchart.node import Node
from flowtutor.flowchart.connection import Connection


class Flowchart:

    def __init__(self):
        self._nodes = []
        self._connections = []

    @property
    def nodes(self) -> list[Node]:
        return self._nodes

    @property
    def connections(self) -> list[Connection]:
        return self._connections

    def find_node(self, tag: str) -> Optional[Node]:
        return next(filter(lambda n: n is not None and n.tag == tag, self.nodes), None)

    def find_hovered_node(self, mouse_position: tuple[int, int]):
        return next(filter(lambda n: n.is_hovered(mouse_position), self.nodes), None)

    def find_connection(self, src_tag: str, index: int):
        return next(filter(lambda c: c.src == src_tag and c.src_ind == int(index), self.connections), None)

    def get_node_children(self, node: Node, cond_count: int = 0, connection_index: Optional[int] = None):
        children: list[Node] = []
        if isinstance(node, Conditional):
            cond_count += 1
        for connection in filter(lambda c: c.src != c.dst and c.src == node.tag
                                 and (connection_index is None or c.src_ind == connection_index), self.connections):
            child = self.find_node(connection.dst)
            if isinstance(child, Connector):
                if cond_count == 1:
                    children.append(child)
                else:
                    children.extend(
                        [child, *self.get_node_children(child, cond_count - 1)])
            elif child is not None:
                children.extend(
                    [child, *self.get_node_children(child, cond_count)])
        return children

    def add_node(self, node: Node, parent: Optional[Node], src_ind: int = 0, dst_ind: int = 0):
        if parent is None:
            pos = (135, 20)
        elif isinstance(node, Connector):
            pos_x, pos_y = parent.pos
            pos = (int(pos_x + parent.width/2 - 25), int(pos_y + 180))
        else:
            _, connection_point_y = parent.out_points[int(src_ind)]
            if isinstance(parent, Conditional):
                if int(src_ind) == 0:
                    pos = (parent.pos[0] - 125, connection_point_y + 80)
                else:
                    pos = (parent.pos[0] + 125, connection_point_y + 80)
            elif isinstance(parent, Loop) and int(src_ind) == 1:
                pos = (parent.pos[0] + 145, connection_point_y + 80)
            else:
                pos = (parent.pos[0], connection_point_y + 80)
        node.pos = pos
        self.nodes.append(node)
        self.move_below(node)
        if isinstance(node, Conditional):
            connector_node = Connector()
            self.add_node(connector_node, node)
            self.nodes.append(connector_node)
            self.add_connection(node.tag, 0, connector_node.tag, 0)
            self.add_connection(node.tag, 1, connector_node.tag, 0)
        elif isinstance(node, Loop):
            self.add_connection(node.tag, 1, node.tag, 1)
        if not isinstance(node, Connector) and parent is not None:
            self.add_connection(parent.tag, src_ind, node.tag, int(dst_ind))

    def add_connection(self, src_tag: str, src_ind: int, dst_tag: str, dst_ind: int):
        existing_connection = self.find_connection(src_tag, src_ind)
        """If there is already a connection on this position, an additional connection is added"""
        if existing_connection is not None:
            self.remove_connection(existing_connection)
            existing_additional_connection = self.find_connection(dst_tag, 0)
            if existing_additional_connection is None:
                additional_connection = Connection(
                    dst_tag, 0, existing_connection.dst, existing_connection.dst_ind)
                self.connections.append(additional_connection)
            else:
                additional_connection = Connection(
                    existing_additional_connection.dst, 0, existing_connection.dst, existing_connection.dst_ind)
                self.connections.append(additional_connection)
        new_connection = Connection(src_tag, int(src_ind), dst_tag, int(dst_ind))
        self.connections.append(new_connection)

    def remove_node(self, node: Optional[Node]):
        if node is None:
            return
        node.delete()
        if self.nodes.__contains__(node):
            self.nodes.remove(node)

    def remove_connection(self, connection: Optional[Connection]):
        if connection is None:
            return
        connection.delete()
        self.connections.remove(connection)

    def move_below(self, node: Optional[Node]):
        if node is None:
            return
        for node_below in [n for n in self.nodes if n.pos[1] > node.pos[1]]:
            pos_x, pos_y = node_below.pos
            node_below.pos = (pos_x, int(pos_y + node.height / 2 + 20))

    def cleanup_connections(self):
        self._connections = list(filter(lambda c: dpg.does_item_exist(
            c.src) and dpg.does_item_exist(c.dst), self.connections))
