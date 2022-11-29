from __future__ import annotations
from typing import TYPE_CHECKING, Generator, Optional, Tuple, Union

from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.connection import Connection
from flowtutor.flowchart.connector import Connector
from flowtutor.flowchart.declaration import Declaration
from flowtutor.flowchart.loop import Loop
from flowtutor.flowchart.input import Input
from flowtutor.flowchart.output import Output
from flowtutor.flowchart.function import Function

if TYPE_CHECKING:
    from flowtutor.flowchart.node import Node


class Flowchart:

    def __init__(self):
        self._lang = 'c'
        root = Function('main')
        root.pos = (290, 20)
        self._root = root
        end = Function('End')
        self.add_node(root, end)

    @property
    def root(self) -> Function:
        return self._root

    @property
    def lang(self) -> str:
        return self._lang

    @lang.setter
    def lang(self, lang: str):
        self._lang = lang

    def __iter__(self):
        return self.deduplicate(self.get_all_nodes(self.root, False))

    def __len__(self):
        return len(list(self.__iter__()))

    def deduplicate(self, it) -> Generator[Node, None, None]:
        seen = set()
        for node in it:
            if node not in seen:
                yield node
                seen.add(node)

    def get_all_nodes(self, node: Node, ignore_span: bool) -> Generator[Node, None, None]:
        yield node
        for connection in sorted(node.connections, key=lambda n: n.src_ind, reverse=True):
            if ((connection.span or ignore_span) and
                    connection.dst_node.tag not in node.scope and node != connection.dst_node):
                yield from self.get_all_nodes(connection.dst_node, ignore_span)

    def get_all_children(self, node: Node, ignore_span: bool) -> Generator[Node, None, None]:
        for connection in sorted(node.connections, key=lambda n: n.src_ind, reverse=True):
            if ((connection.span or ignore_span) and
                    connection.dst_node.tag not in node.scope and node != connection.dst_node):
                yield from self.get_all_nodes(connection.dst_node, ignore_span)

    def get_all_declarations(self) -> Generator[Union[Declaration, Loop], None, None]:
        for node in self:
            if isinstance(node, Declaration):
                yield node
            elif isinstance(node, Loop) and node.loop_type == 'for':
                yield node

    def find_declaration(self, var_name: str) -> Union[Declaration, Loop, None]:
        return next(filter(lambda n: n is not None and n.var_name == var_name, self.get_all_declarations()), None)

    def find_node(self, tag: str) -> Optional[Node]:
        return next(filter(lambda n: n is not None and n.tag == tag, self), None)

    def find_parent(self, node: Node) -> Optional[Node]:
        return next(filter(lambda n: n is not None and any(c.dst_node == node for c in n.connections), self), None)

    def find_successor(self, node: Node) -> Optional[Node]:
        if isinstance(node, Conditional):
            connector = next(filter(lambda n: isinstance(n, Connector)
                             and n.scope and n.scope[-1] == node.tag, self), None)
            if connector is not None:
                connection = connector.find_connection(0)
                return None if connection is None else connection.dst_node
            else:
                return None
        else:
            connection = node.find_connection(0)
            return None if connection is None else connection.dst_node

    def find_hovered_node(self, mouse_position: Tuple[int, int]):
        return next(filter(lambda n: n.is_hovered(mouse_position), self), None)

    def is_initialized(self):
        return all(map(lambda n: n.is_initialized, self))

    def contains_io(self):
        return any(map(lambda n: isinstance(n, Input) or isinstance(n, Output), self))

    def add_node(self, parent: Node, child: Node, src_ind: int = 0):
        child.scope = parent.scope.copy()
        if isinstance(parent, Conditional) or isinstance(parent, Loop) and src_ind == 1:
            child.scope.append(parent.tag)
        elif isinstance(parent, Connector):
            child.scope.pop()

        self.set_start_position(child, parent, src_ind)
        if isinstance(child, Connector):
            # A connector node always has two connections to its parent
            parent.connections.append(Connection(child, 0, True))
            parent.connections.append(Connection(child, 1, False))
        else:
            existing_connection = parent.find_connection(src_ind)
            if existing_connection is None:
                parent.connections.append(Connection(child, src_ind, True))
            else:
                parent.connections.remove(existing_connection)
                parent.connections.append(Connection(child, src_ind, True))
                if not isinstance(child, Conditional):
                    child.connections.append(Connection(existing_connection.dst_node, 0, existing_connection.span))

            if isinstance(child, Conditional):
                connector_node = Connector()
                self.add_node(child, connector_node)
                if existing_connection is not None:
                    connector_node.connections.append(
                        Connection(existing_connection.dst_node, 0, existing_connection.span))
                self.move_below(connector_node)
            elif isinstance(child, Loop):
                child.connections.append(Connection(child, 1, False))
            self.move_below(child)

    def set_start_position(self, node: Node, parent: Node, src_ind: int):  # pragma: no cover
        if isinstance(node, Connector):
            pos_x, pos_y = parent.pos
            pos = (int(pos_x + parent.shape_width/2 - node.shape_width/2),
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
            elif isinstance(parent, Loop):
                pos = (parent.pos[0] - 35, connection_point_y + 50)
            elif isinstance(parent, Connector):
                pos = (parent.pos[0] - parent.shape_width, connection_point_y + 50)
            else:
                pos = (parent.pos[0], connection_point_y + 50)

        node.pos = pos

    def remove_node(self, node: Node):
        if isinstance(node, Connector) or isinstance(node, Function):
            return
        parent = self.find_parent(node)
        if parent is None:
            return
        successor = self.find_successor(node)
        old_src_connection = next(filter(lambda c: c is not None and c.dst_node == node, parent.connections), None)
        if old_src_connection is None:
            return
        parent.connections.remove(old_src_connection)
        if successor is None:
            return
        old_dst_connection = next(filter(lambda c: c is not None and c.dst_node == successor, node.connections), None)
        if old_dst_connection is None:
            parent.connections.append(Connection(successor, old_src_connection.src_ind, True))
        else:
            parent.connections.append(Connection(successor, old_src_connection.src_ind, old_dst_connection.span))

    def move_below(self, parent: Node):  # pragma: no cover
        for i, child in enumerate(self.deduplicate(self.get_all_children(parent, True))):
            if child.tag not in parent.scope:
                pos_x, pos_y = child.pos
                child.pos = (pos_x, int(pos_y + parent.shape_height + 50))
        pass

    def clear(self):
        for node in self:
            node.delete()
