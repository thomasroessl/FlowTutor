from flowtutor.flowchart.flowchart import Flowchart
from flowtutor.flowchart.assignment import Assignment
from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.connector import Connector
from flowtutor.flowchart.declaration import Declaration
from flowtutor.flowchart.function import Function
from flowtutor.flowchart.loop import Loop
from flowtutor.flowchart.input import Input
from flowtutor.flowchart.output import Output
from flowtutor.flowchart.node import Node
from flowtutor.language import Language


class CodeGenerator:

    def generate_code(self, flowchart: Flowchart, node: Node, indent: str = ''):
        if len(node.comment) > 0:
            yield f'{indent}// {node.comment}'
        if isinstance(node, Declaration):
            yield ''.join([
                indent,
                node.var_type,
                ' ',
                '*' if node.is_pointer else '',
                node.var_name,
                f'[{node.array_size}]' if node.is_array else '',
                f' = {node.var_value}' if len(node.var_value) > 0 else '',
                ';'
            ])
        elif isinstance(node, Assignment):
            yield ''.join([f'{indent}{node.var_name}',
                          f'[{node.var_offset}]' if len(node.var_offset) > 0 else '',
                           f' = {node.var_value};'])
        elif isinstance(node, Conditional):
            yield f'{indent}if({node.condition}) {{'
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
                if flowchart.contains_io():
                    yield f'{indent}#include <stdio.h>'
                    yield ''
                yield f'{indent}int {node.name}() {{'
                indent += '  '
        elif isinstance(node, Loop):
            if node.loop_type == 'for':
                yield f'{indent}for(int {node.var_name} = {node.start_value}; {node.condition}; {node.update}) {{'
            else:
                yield f'{indent}while({node.condition}) {{'
            indent += '  '
        elif isinstance(node, Input):
            declaration = flowchart.find_declaration(node.var_name)
            if declaration is None:
                yield f'{indent}// {node.var_name} is not declared!'
            else:
                var_type = 'int' if isinstance(declaration, Loop) else declaration.var_type
                type_formats = list(zip(Language.get_data_types(), Language.get_format_specifiers()))
                _, format_specifier = next(t for t in type_formats if t[0] == var_type)
                yield f'{indent}scanf("{format_specifier}", {node.var_name})'

        elif isinstance(node, Output):
            yield f'{indent}printf("{node.format_string}", {node.expression})'

        for connection in sorted(node.connections, key=lambda n: n.src_ind, reverse=True):
            if isinstance(node, Conditional):
                if connection.src_ind == 0 and not isinstance(connection.dst_node, Connector):
                    yield f'{indent[:len(indent) - 2]}}} else {{'
            elif isinstance(node, Loop):
                if connection.src_ind == 0 and not connection.dst_node == node:
                    indent = indent[:len(indent) - 2]
                    yield f'{indent}}}'
            if (connection.span and connection.dst_node.tag not in node.scope and node != connection.dst_node):
                yield from self.generate_code(flowchart, connection.dst_node, indent)
