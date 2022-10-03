from flowtutor.flowchart.assignment import Assignment
from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.connector import Connector
from flowtutor.flowchart.declaration import Declaration
from flowtutor.flowchart.function import Function
from flowtutor.flowchart.loop import Loop
from flowtutor.flowchart.input import Input
from flowtutor.flowchart.output import Output
from flowtutor.flowchart.node import Node


class CodeGenerator:

    def generate_code(self, node: Node, indent: str = ''):
        if isinstance(node, Declaration):
            yield (f'{indent}{node.var_type}'
                   + (' *' if node.is_pointer else ' ')
                   + node.var_name
                   + (f'[{node.array_size}];' if node.is_array else ';'))
        elif isinstance(node, Assignment):
            yield ''.join([f'{indent}{node.var_name}',
                          f'[{node.var_offset}]' if len(node.var_offset) > 0 else '',
                           f' = {node.var_value};'])
        elif isinstance(node, Conditional):
            yield f'{indent}if ({node.condition}) {{'
            indent += '  '
        elif isinstance(node, Connector):
            indent = indent[:len(indent) - 2]
            yield f'{indent}}}'
        elif isinstance(node, Function):
            if node.name == 'End':
                yield f'{indent}return 0;'
                indent = indent[:len(indent) - 2]
                yield '}'
                return
            else:
                yield f'{indent}int {node.name} () {{'
                indent += '  '
        elif isinstance(node, Loop):
            yield f'{indent}while ({node.condition}) {{'
            indent += '  '
        elif isinstance(node, Input):
            yield f'{indent}scanf("%s", {node.var_name});'
            indent += '  '
        elif isinstance(node, Output):
            yield f'{indent}printf({node.expression});'
            indent += '  '
        else:
            yield f'{indent}{node.label}'

        for connection in sorted(node.connections, key=lambda n: n.src_ind, reverse=True):
            if isinstance(node, Conditional):
                if connection.src_ind == 0 and not isinstance(connection.dst_node, Connector):
                    yield f'{indent[:len(indent) - 2]}}} else {{'
            elif isinstance(node, Loop):
                if connection.src_ind == 0 and not connection.dst_node == node:
                    indent = indent[:len(indent) - 2]
                    yield f'{indent}}}'
            if (connection.span and connection.dst_node.tag not in node.scope and node != connection.dst_node):
                yield from self.generate_code(connection.dst_node, indent)
