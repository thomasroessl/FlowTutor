from typing import Generator, Optional, cast
from os import remove

from flowtutor.flowchart.assignment import Assignment
from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.connector import Connector
from flowtutor.flowchart.declaration import Declaration
from flowtutor.flowchart.flowchart import Flowchart
from flowtutor.flowchart.function import Function
from flowtutor.flowchart.input import Input
from flowtutor.flowchart.loop import Loop
from flowtutor.flowchart.node import Node
from flowtutor.flowchart.output import Output
from flowtutor.language import Language


class CodeGenerator:

    def __init__(self):
        self.prev_source_code = ''
        self.prev_break_points = ''
        try:
            remove('flowtutor_break_points')
        except FileNotFoundError:
            pass
        try:
            remove('flowtutor.c')
        except FileNotFoundError:
            pass

    def write_source_files(self, flowcharts: list[Flowchart]) -> Optional[str]:
        source_code, break_points = self.generate_code(flowcharts)
        if break_points != self.prev_break_points:
            self.prev_break_points = break_points
            with open('flowtutor_break_points', 'w') as file:
                file.write(break_points)
        if source_code != self.prev_source_code:
            self.prev_source_code = source_code
            with open('flowtutor.c', 'w') as file:
                # Add a function to the source code, that turns off stdout buffering
                # Otherwise output will not be displayed until after the program has finished.
                file.write(source_code + '\nvoid fix_debug(void) { setvbuf(stdout, NULL, _IONBF, 0); }')
            return source_code
        else:
            return None

    def generate_code(self, flowcharts: list[Flowchart]) -> tuple[str, str]:
        source: list[tuple[str, bool, Optional[Node]]] = [('#include <stdio.h>', False, None)]

        for flowchart in flowcharts:
            source.append(('', False, None))
            source.extend(self._generate_code(flowchart, flowchart.root))

        code_lines, break_points, nodes = map(list, zip(*source))

        for flowchart in flowcharts:
            for node in flowchart:
                node.lines = []

        for i, node in enumerate(nodes):
            if node is not None:
                cast(Node, node).lines.append(i + 1)

        source_code = '\n'.join(cast(list[str], code_lines))
        break_point_definitions = '\n'.join(
            map(lambda e: f'break flowtutor.c:{e[0] + 1}',
                filter(lambda e: e[1],
                       enumerate(break_points))))

        return (source_code, break_point_definitions)

    def _generate_code(self, flowchart: Flowchart, node: Node, indent: str = '') -> \
            Generator[tuple[str, bool, Node], None, None]:
        if len(node.comment) > 0:
            yield (f'{indent}// {node.comment}', False, node)
        if isinstance(node, Declaration):
            yield (''.join([
                indent,
                node.var_type,
                ' ',
                '*' if node.is_pointer else '',
                node.var_name,
                f'[{node.array_size}]' if node.is_array else '',
                f' = {node.var_value}' if len(node.var_value) > 0 else '',
                ';'
            ]), node.break_point, node)
        elif isinstance(node, Assignment):
            yield (''.join([f'{indent}{node.var_name}',
                            f'[{node.var_offset}]' if len(node.var_offset) > 0 else '',
                           f' = {node.var_value};']), node.break_point, node)
        elif isinstance(node, Conditional):
            yield (f'{indent}if({node.condition}) {{', node.break_point, node)
            indent += '  '
        elif isinstance(node, Connector):
            indent = indent[:len(indent) - 2]
            yield (f'{indent}}}', False, node)
        elif isinstance(node, Function):
            if node.name == 'End':
                yield (f'{indent}return 0;', node.break_point, node)
                indent = indent[:len(indent) - 2]
                yield ('}', False, node)
                return
            else:
                yield (f'{indent}int {node.name}() {{', node.break_point, node)
                indent += '  '
        elif isinstance(node, Loop):
            if node.loop_type == 'for':
                yield (f'{indent}for(int {node.var_name} = {node.start_value}; {node.condition}; {node.update}) {{',
                       node.break_point, node)
            else:
                yield (f'{indent}while({node.condition}) {{', node.break_point, node)
            indent += '  '
        elif isinstance(node, Input):
            declaration = flowchart.find_declaration(node.var_name)
            if declaration is None:
                yield (f'{indent}// {node.var_name} is not declared!', False, node)
            else:
                var_type = 'int' if isinstance(declaration, Loop) else declaration.var_type
                type_formats = list(zip(Language.get_data_types(), Language.get_format_specifiers()))
                _, format_specifier = next(t for t in type_formats if t[0] == var_type)
                yield (f'{indent}scanf("{format_specifier}", {node.var_name});', node.break_point, node)

        elif isinstance(node, Output):
            if len(node.arguments) > 0:
                yield (f'{indent}printf("{node.format_string}", {node.arguments});', node.break_point, node)
            else:
                yield (f'{indent}printf("{node.format_string}");', node.break_point, node)

        for connection in sorted(node.connections, key=lambda n: n.src_ind, reverse=True):
            if isinstance(node, Conditional):
                if connection.src_ind == 0 and not isinstance(connection.dst_node, Connector):
                    yield (f'{indent[:len(indent) - 2]}}} else {{', False, node)
            elif isinstance(node, Loop):
                if connection.src_ind == 0 and not connection.dst_node == node:
                    indent = indent[:len(indent) - 2]
                    yield (f'{indent}}}', False, node)
            if (connection.span and connection.dst_node.tag not in node.scope and node != connection.dst_node):
                yield from self._generate_code(flowchart, connection.dst_node, indent)
