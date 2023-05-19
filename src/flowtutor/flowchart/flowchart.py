from __future__ import annotations
from typing import TYPE_CHECKING, Any, Generator, Optional
from shapely.geometry import box

from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.connection import Connection
from flowtutor.flowchart.connector import Connector
from flowtutor.flowchart.declaration import Declaration
from flowtutor.flowchart.declarations import Declarations
from flowtutor.flowchart.dowhileloop import DoWhileLoop
from flowtutor.flowchart.forloop import ForLoop
from flowtutor.flowchart.functionstart import FunctionStart
from flowtutor.flowchart.functionend import FunctionEnd
from flowtutor.flowchart.struct_definition import StructDefinition
from flowtutor.flowchart.type_definition import TypeDefinition
from flowtutor.flowchart.whileloop import WhileLoop

if TYPE_CHECKING:
    from flowtutor.flowchart.node import Node


class Flowchart:

    def __init__(self, name: str):
        root = FunctionStart(name)
        root.pos = (290, 20)
        self._root = root
        end = FunctionEnd(name)
        self.add_node(root, end)
        self._includes: list[str] = ['stdio']
        self._preprocessor_definitions: list[str] = []
        self._type_definitions: list[TypeDefinition] = []
        self._struct_definitions: list[StructDefinition] = []
        self._preprocessor_custom: str = ''

    @property
    def root(self) -> FunctionStart:
        return self._root

    @property
    def includes(self) -> list[str]:
        return self._includes

    @property
    def preprocessor_definitions(self) -> list[str]:
        return self._preprocessor_definitions

    @property
    def type_definitions(self) -> list[TypeDefinition]:
        return self._type_definitions

    @property
    def struct_definitions(self) -> list[StructDefinition]:
        return self._struct_definitions

    @property
    def preprocessor_custom(self) -> str:
        return self._preprocessor_custom

    @preprocessor_custom.setter
    def preprocessor_custom(self, preprocessor_custom: str) -> None:
        self._preprocessor_custom = preprocessor_custom

    def __iter__(self) -> Generator[Node, None, None]:
        return self.deduplicate(self.get_all_nodes(self.root, False))

    def __len__(self) -> int:
        return len(list(self.__iter__()))

    def deduplicate(self, it: Generator[Node, None, None]) -> Generator[Node, None, None]:
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

    def get_function_declaration(self) -> str:
        parameters = ', '.join([str(p) for p in self.root.parameters])
        return f'{self.root.return_type} {self.root.name}({parameters});'

    def get_all_declarations(self) -> Generator[dict[str, Any], None, None]:
        for node in self:
            if isinstance(node, Declaration):
                yield node.get_declaration()
            elif isinstance(node, Declarations):
                for declaration in node.declarations:
                    yield declaration
            elif isinstance(node, ForLoop):
                yield node.get_declaration()

    def find_declaration(self, var_name: str) -> Optional[dict[str, Any]]:
        return next(filter(lambda n: n and n['var_name'] == var_name, self.get_all_declarations()), None)

    def find_node(self, tag: str) -> Optional[Node]:
        return next(filter(lambda n: n is not None and n.tag == tag, self), None)

    def find_parent(self, node: Node) -> Optional[Node]:
        return next(filter(lambda n: n is not None and any(c.dst_node == node for c in n.connections), self), None)

    def find_containing_node(self, child: Node) -> Optional[Node]:
        '''Gets the node, that contains the child node (loop, conditional, etc.)'''
        current_parent = self.find_parent(child)
        while current_parent:
            if current_parent.tag in child.scope:
                return current_parent
            else:
                current_parent = self.find_parent(current_parent)
        return None

    def find_nodes_in_selection(self, pmin: tuple[float, float], pmax: tuple[float, float]) -> list[Node]:
        selection_box = box(*pmin, *pmax)
        return list(filter(lambda n: n.shape.intersects(selection_box), self))

    def find_successor(self, node: Node) -> Optional[Node]:
        if isinstance(node, Conditional):
            connector = next(filter(lambda n: isinstance(n, Connector)
                             and n.scope and n.scope[-1] == node.tag, self), None)
            if connector:
                connection = connector.find_connection(0)
                return None if not connection else connection.dst_node
            else:
                return None
        else:
            connection = node.find_connection(0)
            return None if not connection else connection.dst_node

    def find_hovered_node(self, mouse_position: Optional[tuple[int, int]]) -> Optional[Node]:
        return next(filter(lambda n: n is not None and n.is_hovered(mouse_position), self), None) \
            if mouse_position else None

    def is_initialized(self) -> bool:
        return all(map(lambda n: n.is_initialized, self))

    def add_node(self, parent: Node, child: Node, src_ind: int = 0) -> None:
        child.scope = parent.scope.copy()
        if isinstance(parent, Conditional) or\
            (isinstance(parent, ForLoop) or
             isinstance(parent, WhileLoop) or
             isinstance(parent, DoWhileLoop))\
                and src_ind == 1:
            child.scope.append(parent.tag)
        elif isinstance(parent, Connector) and child.scope:
            child.scope.pop()

        self.set_start_position(child, parent, src_ind)
        if isinstance(child, Connector):
            # A connector node always has two connections to its parent
            parent.connections.append(Connection(child, 0, True))
            parent.connections.append(Connection(child, 1, False))
        else:
            existing_connection = parent.find_connection(src_ind)
            if not existing_connection:
                parent.connections.append(Connection(child, src_ind, True))
            else:
                parent.connections.remove(existing_connection)
                parent.connections.append(Connection(child, src_ind, True))
                if not isinstance(child, Conditional):
                    child.connections.append(Connection(existing_connection.dst_node, 0, existing_connection.span))

            if isinstance(child, Conditional):
                connector_node = Connector()
                self.add_node(child, connector_node)
                if existing_connection:
                    connector_node.connections.append(
                        Connection(existing_connection.dst_node, 0, existing_connection.span))
                self.move_below(connector_node)
            elif isinstance(child, ForLoop) or isinstance(child, WhileLoop) or isinstance(child, DoWhileLoop):
                child.connections.append(Connection(child, 1, False))
            self.move_below(child)

    def set_start_position(self, node: Node, parent: Node, src_ind: int) -> None:  # pragma: no cover
        if isinstance(node, Connector):
            pos_x, pos_y = parent.pos
            pos = (int(pos_x + parent.shape_width/2 - node.shape_width/2),
                   int(pos_y))
        else:
            _, connection_point_y = parent.out_points[int(src_ind)]
            if isinstance(parent, Conditional):
                if int(src_ind) == 0:
                    pos = (parent.pos[0] - 125, int(connection_point_y + 50))
                else:
                    pos = (parent.pos[0] + 125, int(connection_point_y + 50))
            elif (isinstance(parent, ForLoop) or isinstance(parent, WhileLoop) or isinstance(parent, DoWhileLoop)) and\
                    int(src_ind) == 1:
                pos = (parent.pos[0] + 160, int(connection_point_y + 25))
            elif (isinstance(parent, ForLoop) or isinstance(parent, WhileLoop) or isinstance(parent, DoWhileLoop)):
                pos = (parent.pos[0] - 35, int(connection_point_y + 50))
            elif isinstance(parent, Connector):
                pos = (parent.pos[0] - parent.shape_width, int(connection_point_y + 50))
            else:
                pos = (parent.pos[0], int(connection_point_y + 50))

        node.pos = pos

    def remove_node(self, node: Node) -> None:
        if isinstance(node, Connector) or isinstance(node, FunctionStart) or isinstance(node, FunctionEnd):
            return
        parent = self.find_parent(node)
        if not parent:
            return
        successor = self.find_successor(node)
        old_src_connection = next(filter(lambda c: c is not None and c.dst_node == node, parent.connections), None)
        if not old_src_connection:
            return
        parent.connections.remove(old_src_connection)
        if not successor:
            return
        old_dst_connection = next(filter(lambda c: c is not None and c.dst_node == successor, node.connections), None)
        if not old_dst_connection:
            parent.connections.append(Connection(successor, old_src_connection.src_ind, True))
        else:
            parent.connections.append(Connection(successor, old_src_connection.src_ind, old_dst_connection.span))

    def move_below(self, parent: Node) -> None:  # pragma: no cover
        ''' Moves ol children of a node down, so they do not overlap.'''
        children = list(self.deduplicate(self.get_all_children(parent, True)))
        if not children:
            return
        min_pos_y = parent.pos[1] + parent.shape_height + 50
        _, child_pos_y = children[0].pos
        distance = min_pos_y - child_pos_y
        if distance > 0:
            for child in filter(lambda c: c.tag not in parent.scope, children):
                pos_x, pos_y = child.pos
                child.pos = (pos_x, pos_y + distance)

    def clear(self) -> None:
        for node in self:
            node.delete()

    def reset(self) -> None:
        name = self._root.name
        root = FunctionStart(name)
        root.pos = (290, 20)
        self._root = root
        end = FunctionEnd(name)
        self.add_node(root, end)
