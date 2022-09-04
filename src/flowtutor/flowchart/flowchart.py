from typing import Optional
from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.connection import Connection
from flowtutor.flowchart.connector import Connector
from flowtutor.flowchart.loop import Loop
from flowtutor.flowchart.node import Node
from flowtutor.flowchart.root import Root


class Flowchart:

    def __init__(self):
        root = Root()
        root.pos = (135, 20)
        self._root = root

    @property
    def root(self) -> Node:
        return self._root

    def __iter__(self):
        return self.deduplicate(self.get_all_nodes(self.root))

    def __len__(self):
        return len(list(self.__iter__()))

    def deduplicate(self, it):
        seen = set()
        for x in it:
            if x not in seen:
                yield x
                seen.add(x)

    def get_all_nodes(self, node: Node):
        yield node
        for connection in node.connections:
            if connection.dst_node.tag not in node.scope and node != connection.dst_node:
                yield from self.get_all_nodes(connection.dst_node)

    def get_all_children(self, node: Node):
        for connection in node.connections:
            yield from self.get_all_nodes(connection.dst_node)

    def find_node(self, tag: str) -> Optional[Node]:
        return next(filter(lambda n: n is not None and n.tag == tag, self), None)

    def find_hovered_node(self, mouse_position: tuple[int, int]):
        return next(filter(lambda n: n.is_hovered(mouse_position), self), None)

    def add_node(self, parent: Node, child: Node, src_ind: int = 0):

        child.scope = parent.scope.copy()
        if isinstance(parent, Conditional) or isinstance(parent, Loop) and src_ind == 1:
            child.scope.append(parent.tag)
        elif isinstance(parent, Connector):
            child.scope.pop()

        self.set_start_position(child, parent, src_ind)
        if isinstance(child, Connector):
            # A connector node always has two connections to its parent
            parent.connections.append(Connection(child, 0))
            parent.connections.append(Connection(child, 1))
        else:
            existing_connection = parent.find_connection(src_ind)
            if existing_connection is None:
                parent.connections.append(Connection(child, src_ind))
            else:
                parent.connections.remove(existing_connection)
                parent.connections.append(Connection(child, src_ind))
                if not isinstance(child, Conditional):
                    child.connections.append(Connection(existing_connection.dst_node, 0))

            if isinstance(child, Conditional):
                connector_node = Connector()
                self.add_node(child, connector_node)
                if existing_connection is not None:
                    connector_node.connections.append(Connection(existing_connection.dst_node, 0))
                self.move_below(connector_node)
            elif isinstance(child, Loop):
                child.connections.append(Connection(child, 1))
            self.move_below(child)

    def set_start_position(self, node: Node, parent: Node, src_ind: int):
        if isinstance(node, Connector):
            pos_x, pos_y = parent.pos
            pos = (int(pos_x + parent.width/2 - node.width/2),
                   int(pos_y))
        else:
            _, connection_point_y = parent.out_points[int(src_ind)]
            if isinstance(parent, Conditional):
                if int(src_ind) == 0:
                    pos = (parent.pos[0] - 125, connection_point_y + 50)
                else:
                    pos = (parent.pos[0] + 125, connection_point_y + 50)
            elif isinstance(parent, Loop) and int(src_ind) == 1:
                pos = (parent.pos[0] + 145, connection_point_y + 50)
            elif isinstance(parent, Connector):
                pos = (parent.pos[0] - parent.width, connection_point_y + 50)
            else:
                pos = (parent.pos[0], connection_point_y + 50)

        node.pos = pos

    def remove_node(self, node: Optional[Node]):
        if node is None:
            return

        node.delete()
        # if node in self.nodes:
        #     self.nodes.remove(node)

    def move_below(self, parent: Node):
        for child in self.deduplicate(self.get_all_children(parent)):
            if child != parent and child.tag not in parent.scope:
                pos_x, pos_y = child.pos
                child.pos = (pos_x, int(pos_y + parent.height + 50))
        pass
