from __future__ import annotations
from typing import TYPE_CHECKING, Generator, Optional, cast
from dependency_injector.wiring import Provide, inject

from flowtutor.flowchart.connector import Connector
from flowtutor.flowchart.flowchart import Flowchart
from flowtutor.flowchart.functionstart import FunctionStart
from flowtutor.flowchart.functionend import FunctionEnd
from flowtutor.flowchart.node import Node
from flowtutor.flowchart.template import Template

if TYPE_CHECKING:
    from flowtutor.language_service import LanguageService
    from flowtutor.util_service import UtilService


class CodeGenerator:

    @inject
    def __init__(self,
                 utils_service: UtilService = Provide['utils_service'],
                 language_service: LanguageService = Provide['language_service']):
        self.prev_source_code = ''
        self.prev_break_points = ''
        self.utils = utils_service
        self.language_service = language_service

    def write_source_file(self, flowcharts: list[Flowchart]) -> Optional[str]:
        source_code, break_points = self.generate_code(flowcharts)
        flowcharts[0].break_points = break_points
        if source_code != self.prev_source_code:
            self.prev_source_code = source_code
            with open(self.utils.get_source_path(flowcharts[0].lang_data['file_ext']), 'w') as file:
                file.write(source_code)
            return source_code
        else:
            return None

    def generate_code(self, flowcharts: list[Flowchart]) -> tuple[str, list[int]]:
        main_function = flowcharts[0]
        functions = flowcharts[1:]

        source: list[tuple[str, Optional[Node]]] = self.language_service.render_imports(main_function)
        if len(source) > 0 and source[-1][0]:
            source.append(('', None))
        for type_definition in main_function.type_definitions:
            source += [
                (str(type_definition), None)
            ]
        for struct_definition in main_function.struct_definitions:
            if len(source) > 0 and source[-1][0]:
                source += [('', None)]
            source += [
                (d, None) for d in str(struct_definition).split('\n')
            ]
        source += [
            (f'#define {d}', None) for d in main_function.preprocessor_definitions
        ]
        if main_function.preprocessor_custom:
            source += [
                (c, None) for c in main_function.preprocessor_custom.split('\n')
            ]
        if len(source) > 0 and source[-1][0]:
            source.append(('', None))

        for flowchart in functions:
            source.extend(self.language_service.render_function_declaration(main_function, flowchart.root))

        if self.language_service.has_function_declarations(main_function):
            all_flowcharts = flowcharts
        else:
            all_flowcharts = functions + [main_function]

        for i, flowchart in enumerate(all_flowcharts):
            if len(source) > 0 and source[-1][0]:
                source.append(('', None))
            source.extend(self._generate_code(flowchart, flowchart.root, set(), False))

        nodes: list[Optional[Node]] = []
        code_lines: list[str] = []
        if source:
            code_lines, nodes = map(list, zip(*source))  # type: ignore

        for flowchart in all_flowcharts:
            for n in flowchart:
                n.lines = []

        for i, n1 in enumerate(nodes):
            if n1:
                n1.lines.append(i + 1)

        source_code = '\n'.join(code_lines)

        break_points = list(
            map(lambda n: cast(Node, n).lines[0],
                filter(lambda n: n and n.break_point, nodes)))

        return (source_code, break_points)

    def _generate_code(self,
                       flowchart: Flowchart,
                       node: Node,
                       visited_nodes: set[Node],
                       is_branch: bool) -> Generator[tuple[str, Optional[Node]], None, None]:
        visited_nodes.add(node)
        if isinstance(node, Template):
            loop_body: list[tuple[str, Optional[Node]]] = []
            if_branch: list[tuple[str, Optional[Node]]] = []
            else_branch: list[tuple[str, Optional[Node]]] = []
            if node.control_flow == 'loop' or node.control_flow == 'post-loop':
                loop_body = sum([list(self._generate_code(flowchart, c.dst_node, visited_nodes, False))
                                 for c in node.connections if c.src_ind == 1 and c.dst_node not in visited_nodes], [])
            elif node.control_flow == 'decision':
                for c in [c for c in node.connections if c.src_ind == 1 and c.dst_node not in visited_nodes]:
                    if_branch.extend(self._generate_code(flowchart, c.dst_node, visited_nodes, True))
                for c in [c for c in node.connections if c.src_ind == 0 and c.dst_node not in visited_nodes]:
                    else_branch.extend(self._generate_code(flowchart, c.dst_node, visited_nodes, True))
            yield from self.language_service.render_template(node, flowchart, loop_body, if_branch, else_branch)
            if node.control_flow == 'decision':
                successor = flowchart.find_successor(node)
                if successor:
                    yield from self._generate_code(flowchart, successor, visited_nodes, is_branch)
        elif isinstance(node, FunctionStart) and\
                (node.name != 'main' or self.language_service.has_main_function(flowchart)):
            body: list[tuple[str, Optional[Node]]] = []
            body = sum([list(self._generate_code(flowchart, c.dst_node, visited_nodes, False))
                        for c in node.connections if c.src_ind == 0 and c.dst_node not in visited_nodes], [])
            function_end = flowchart.find_function_end()
            yield from self.language_service.render_function(node, function_end, flowchart, body)
        elif isinstance(node, FunctionEnd):
            return
        elif isinstance(node, Connector):
            visited_nodes.remove(node)
            if is_branch:
                return
        for code in [self._generate_code(flowchart, c.dst_node, visited_nodes, is_branch)
                     for c in node.connections if c.src_ind == 0 and c.dst_node not in visited_nodes]:
            yield from code
