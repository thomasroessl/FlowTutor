from __future__ import annotations
from typing import TYPE_CHECKING, Any, Generator, Optional
from shapely.geometry import box, Point

from flowtutor.flowchart.connection import Connection
from flowtutor.flowchart.connector import Connector
from flowtutor.flowchart.functionstart import FunctionStart
from flowtutor.flowchart.functionend import FunctionEnd
from flowtutor.flowchart.struct_definition import StructDefinition
from flowtutor.flowchart.type_definition import TypeDefinition
from flowtutor.flowchart.template import Template

if TYPE_CHECKING:
    from flowtutor.flowchart.node import Node


class Flowchart:
    '''This class represents a flowchart.

       The main function of the program is a flowchart and all defined function have their own flowchart object.'''

    def __init__(self, name: str, lang_data: dict[str, Any]):
        '''Flowchart constructor.

        Parameters:
            name (str): The name of the function this flowchart represents.
            lang_data (dict[str, Any]): The language definition settings.'''
        root = FunctionStart(name)
        root.pos = (290, 20)
        self._root = root
        end = FunctionEnd(name)
        self.add_node(root, end)
        self._imports: list[str] = []
        self._preprocessor_definitions: list[str] = []
        self._type_definitions: list[TypeDefinition] = []
        self._struct_definitions: list[StructDefinition] = []
        self._preprocessor_custom: str = ''
        self.lang_data = lang_data
        self._break_points: list[int] = []

    @property
    def root(self) -> FunctionStart:
        '''The root node of the flowchart.'''
        return self._root

    @property
    def imports(self) -> list[str]:
        '''A list of modules that are importet into the program.'''
        return self._imports

    @property
    def preprocessor_definitions(self) -> list[str]:
        '''A list of preprocessor definitions that get inserted at the start of the generated sourc code file.'''
        return self._preprocessor_definitions

    @property
    def type_definitions(self) -> list[TypeDefinition]:
        '''A list of type definitions that get inserted at the start of the generated sourc code file.'''
        return self._type_definitions

    @property
    def struct_definitions(self) -> list[StructDefinition]:
        '''A list of struct definitions that get inserted at the start of the generated sourc code file.'''
        return self._struct_definitions

    @property
    def preprocessor_custom(self) -> str:
        '''Custom code, to be inserted  at the start of the generated source code file.'''
        return self._preprocessor_custom

    @preprocessor_custom.setter
    def preprocessor_custom(self, preprocessor_custom: str) -> None:
        self._preprocessor_custom = preprocessor_custom

    @property
    def lang_data(self) -> dict[str, Any]:
        '''The language definition settings.'''
        return self._lang_data

    @lang_data.setter
    def lang_data(self, lang_data: dict[str, Any]) -> None:
        self._lang_data = lang_data

    @property
    def break_points(self) -> list[int]:
        '''The line indices in the generated source code file of break points in the flowchart.'''
        return self._break_points

    @break_points.setter
    def break_points(self, break_points: list[int]) -> None:
        self._break_points = break_points

    def __iter__(self) -> Generator[Node, None, None]:
        return self.deduplicate(self.get_all_nodes(self.root))

    def __len__(self) -> int:
        return len(list(self.__iter__()))

    def deduplicate(self, it: Generator[Node, None, None]) -> Generator[Node, None, None]:
        '''Takes an generator of Nodes and removes duplicates.

        Parameters:
            it (Generator[Node, None, None]): The generator to deduplicate.
        '''
        seen = set()
        for node in it:
            if node not in seen:
                yield node
                seen.add(node)

    def get_all_nodes(self, node: Node) -> Generator[Node, None, None]:
        '''Gets all nodes after a specified node, including the node itself.

        Parameters:
            node (Node): The parent node.
        '''
        yield node
        for connection in sorted(node.connections, key=lambda n: n.src_ind, reverse=True):
            if (connection.dst_node.tag not in node.scope and node != connection.dst_node):
                yield from self.get_all_nodes(connection.dst_node)

    def get_all_children(self, node: Node) -> Generator[Node, None, None]:
        '''Gets all nodes after a specified node, excluding the node itself.

        Parameters:
            node (Node): The parent node.
        '''
        for connection in sorted(node.connections, key=lambda n: n.src_ind, reverse=True):
            if (connection.dst_node.tag not in node.scope and node != connection.dst_node):
                yield from self.get_all_nodes(connection.dst_node)

    def find_node(self, tag: str) -> Optional[Node]:
        '''Finds the node instance of a specified tag.

        Parameters:
            tag (str): The tag of the searched node.
        '''
        return next(filter(lambda n: n is not None and n.tag == tag, self), None)

    def find_parent(self, node: Node) -> Optional[Node]:
        '''Finds the parent of a node in the flowchart.

        Parameters:
            node (Node): The child node to find the parent for.
        '''
        return next(filter(lambda n: n is not None and any(c.dst_node == node for c in n.connections), self), None)

    def find_function_end(self) -> FunctionEnd:
        '''Finds the function end node of the flowchart.'''
        node = next(filter(lambda n: isinstance(n, FunctionEnd), self), None)
        if isinstance(node, FunctionEnd):
            return node
        else:
            raise Exception('Flowchart does not contain a function end.')

    def find_parents(self, node: Node) -> list[Node]:
        '''Finds a parents connected to a node.

        Parameters:
            node (Node): The child node to find parents for.
        '''
        return list(filter(lambda n: n is not None and any(c.dst_node == node for c in n.connections), self))

    def find_containing_node(self, child: Node) -> Optional[Node]:
        '''Gets the node, that contains the child node (loop, conditional, etc.)

        Parameters:
            child (Node): The child to find the containing node to.
        '''
        current_parent = self.find_parent(child)
        while current_parent:
            if current_parent.tag in child.scope:
                return current_parent
            else:
                current_parent = self.find_parent(current_parent)
        return None

    def find_nodes_in_selection(self, pmin: tuple[float, float], pmax: tuple[float, float]) -> list[Node]:
        '''Finds all nodes in a bounding box in the drawing area.

        Parameters:
            pmin(tuple[float, float]): The min point of the bounding box.
            pmax(tuple[float, float]): The max point of the bounding box.
        '''
        selection_box = box(*pmin, *pmax)
        return list(filter(lambda n: n.shape.intersects(selection_box), self))

    def find_successor(self, node: Node) -> Optional[Node]:
        '''Finds the successor node of the curtrent node.

        For decision nodes, this means the node after the decision branches.
        '''
        if isinstance(node, Template) and node.control_flow == 'decision':
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
        '''Finds the node at a specific mouse position in the drawing area.

        Parameters:
            mouse_position (Optional[tuple[int, int]]): The mouse position int the application window.
        '''
        return next(filter(lambda n: n is not None and n.shape.contains(Point(*mouse_position)), self), None) \
            if mouse_position else None

    def is_initialized(self) -> bool:
        '''The flowchart is initialized, when all nodes are initialized.

        A node is initialized, when the user has entered all required parameters.
        '''
        return all(map(lambda n: n.is_initialized, self))

    def add_node(self, parent: Node, child: Node, src_ind: int = 0) -> None:
        '''Adds a node to the flowchart.

        Parameters:
            parent (Node): The node after which the new node should be inserted.
            child (Node): The new node to be inserted.
            src_ind (int): The index of the connection point, at which the node is inserted.
        '''
        # The new node starts with the same scope as its parent.
        child.scope = parent.scope.copy()
        if (isinstance(parent, Template) and parent.control_flow == 'decision') or\
           (isinstance(parent, Template) and (parent.control_flow == 'loop' or parent.control_flow == 'post-loop'))\
                and src_ind == 1:
            # If the node gets inserted into a decision branch, or a loop body, then the parent gets added to its scope.
            child.scope.append(parent.tag)
        elif isinstance(parent, Connector) and child.scope:
            # If the node gets inserted after a connector, this means the flowchart leaves a decision block and
            # therefor an element is removed from the scope.
            child.scope.pop()

        self.set_start_position(child, parent, src_ind)

        # parent and child node need to be redrawn to refresh the connection lines.
        parent.needs_refresh = True
        child.needs_refresh = True
        if isinstance(child, Connector):
            # A connector node always has two connections to its parent
            parent.connections.append(Connection(child, 0))
            parent.connections.append(Connection(child, 1))
        else:
            existing_connection = parent.find_connection(src_ind)
            if not existing_connection:
                parent.connections.append(Connection(child, src_ind))
            else:
                # If the node gets inserted between an existing connection, then it gets removed and the connection
                # are correctly reinserted.
                parent.connections.remove(existing_connection)
                parent.connections.append(Connection(child, src_ind))
                if not (isinstance(child, Template) and child.control_flow == 'decision'):
                    child.connections.append(Connection(existing_connection.dst_node, 0))

            if isinstance(child, Template) and child.control_flow == 'decision':
                # If the inserted node is a decision, then a connector gets inserted after it, and connected to it.
                connector_node = Connector()
                self.add_node(child, connector_node)
                if existing_connection:
                    connector_node.connections.append(
                        Connection(existing_connection.dst_node, 0))
                # The following nodes are moved down accordingly.
                self.move_below(connector_node)
            elif isinstance(child, Template) and (child.control_flow == 'loop' or child.control_flow == 'post-loop'):
                # If the inserted node is a decision, a connection to itself is inserted.
                child.connections.append(Connection(child, 1))
            # The following nodes are moved down accordingly.
            self.move_below(child)

    def set_start_position(self, node: Node, parent: Node, src_ind: int) -> None:  # pragma: no cover
        '''Sets the starting position of a node, relative to its parent.

        Parameters:
            node (Node): The node to set the position of.
            parent (Node): The parent of the node.
            src_ind (int): The connection index of the parent to the node.
        '''
        if isinstance(node, Connector):
            pos_x, pos_y = parent.pos
            pos = (int(pos_x + parent.shape_width/2 - node.shape_width/2),
                   int(pos_y))
        else:
            _, connection_point_y = parent.out_points[int(src_ind)]
            if isinstance(parent, Template) and parent.control_flow == 'decision':
                if int(src_ind) == 0:
                    pos = (parent.pos[0] - 125, int(connection_point_y + 50))
                else:
                    pos = (parent.pos[0] + 125, int(connection_point_y + 50))
            elif (isinstance(parent, Template) and
                  (parent.control_flow == 'loop' or parent.control_flow == 'post-loop')) and int(src_ind) == 1:
                pos = (parent.pos[0] + 160, int(connection_point_y + 25))
            elif (isinstance(parent, Template) and
                  (parent.control_flow == 'loop' or parent.control_flow == 'post-loop')):
                pos = (parent.pos[0] - 35, int(connection_point_y + 50))
            elif isinstance(parent, Connector):
                pos = (parent.pos[0] - parent.shape_width, int(connection_point_y + 50))
            else:
                pos = (parent.pos[0], int(connection_point_y + 50))

        node.pos = pos

    def remove_node(self, node: Node) -> None:
        '''Removes a node from the flwochart and corrects the connections accordingly.

        Every flowchart need start and end nodes, so they cannot be removed.
        Connectors are removed with their parent decision, and cannot be removed on their own.

        Parameters:
            node (Node): The node to remove.
        '''
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
            parent.connections.append(Connection(successor, old_src_connection.src_ind))
        else:
            parent.connections.append(Connection(successor, old_src_connection.src_ind))

    def move_below(self, parent: Node) -> None:  # pragma: no cover
        '''Moves all children of a node down, so they do not overlap.

        Parameters:
            parent (Node): The node aftwer which all nodes get shifted down.
        '''
        children = list(self.deduplicate(self.get_all_children(parent)))
        if not children:
            return
        min_pos_y = parent.pos[1] + parent.shape_height + 50
        if isinstance(parent, Template) and parent.control_flow == 'post-loop':
            min_pos_y += 100
        _, child_pos_y = children[0].pos
        distance = min_pos_y - child_pos_y
        if distance > 0:
            for child in filter(lambda c: c.tag not in parent.scope, children):
                pos_x, pos_y = child.pos
                child.pos = (pos_x, pos_y + distance)
                child.needs_refresh = True
                parents = self.find_parents(child)
                for parent in parents:
                    parent.needs_refresh = True

    def clear(self) -> None:
        '''Clears the drawing area.'''
        for node in self:
            node.delete()

    def reset(self) -> None:
        '''Resets the flowchart to a minimal state.'''
        name = self._root.name
        root = FunctionStart(name)
        root.pos = (290, 20)
        self._root = root
        end = FunctionEnd(name)
        self.add_node(root, end)
