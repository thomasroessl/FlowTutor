from __future__ import annotations
from typing import Any, Generator, Optional, cast
from os import remove, path
from dependency_injector.wiring import Provide, inject


from flowtutor.flowchart.assignment import Assignment
from flowtutor.flowchart.call import Call
from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.connector import Connector
from flowtutor.flowchart.declaration import Declaration
from flowtutor.flowchart.declarations import Declarations
from flowtutor.flowchart.dowhileloop import DoWhileLoop
from flowtutor.flowchart.flowchart import Flowchart
from flowtutor.flowchart.forloop import ForLoop
from flowtutor.flowchart.functionstart import FunctionStart
from flowtutor.flowchart.functionend import FunctionEnd
from flowtutor.flowchart.input import Input
from flowtutor.flowchart.node import Node
from flowtutor.flowchart.output import Output
from flowtutor.flowchart.snippet import Snippet
from flowtutor.flowchart.whileloop import WhileLoop
from flowtutor.flowchart.template import Template
from flowtutor.language import Language
from flowtutor.util_service import UtilService
from flowtutor.template_service import TemplateService


class CodeGenerator:

    @inject
    def __init__(self, 
                utils_service: UtilService = Provide['utils_service'],
                template_service: TemplateService = Provide['template_service']):
        self.prev_source_code = ''
        self.prev_break_points = ''
        self.utils = utils_service
        self.break_point_path = self.utils.get_break_points_path()
        self.template_service = template_service
        try:
            remove(self.break_point_path)
        except FileNotFoundError:
            pass
        try:
            remove(self.utils.get_c_source_path())
        except FileNotFoundError:
            pass

    def write_source_files(self, flowcharts: list[Flowchart]) -> Optional[str]:
        source_code, break_points = self.generate_code(flowcharts)
        if break_points != self.prev_break_points or not path.exists(self.break_point_path):
            self.prev_break_points = break_points
            with open(self.break_point_path, 'w') as file:
                file.write(break_points)
        if source_code != self.prev_source_code:
            self.prev_source_code = source_code
            with open(self.utils.get_c_source_path(), 'w') as file:
                # Add a function to the source code, that turns off stdout buffering
                # Otherwise output will not be displayed until after the program has finished.
                file.write(source_code + '\nvoid fix_debug(void) { setvbuf(stdout, NULL, _IONBF, 0); }')
            return source_code
        else:
            return None

    def generate_code(self, flowcharts: list[Flowchart]) -> tuple[str, str]:
        source: list[tuple[str, bool, Optional[Node]]] = [
            (f'#include <{h}.h>', False, None) for h in flowcharts[0].includes
        ]

        if len(flowcharts[0].type_definitions) > 0:
            source.append(('', False, None))

        for type_definition in flowcharts[0].type_definitions:
            source += [
                (str(type_definition), False, None)
            ]

        for struct_definition in flowcharts[0].struct_definitions:
            source += [('', False, None)]
            source += [
                (d, False, None) for d in str(struct_definition).split('\n')
            ]
        source += [
            (f'#define {d}', False, None) for d in flowcharts[0].preprocessor_definitions
        ]
        if flowcharts[0].preprocessor_custom:
            source += [
                (c, False, None) for c in flowcharts[0].preprocessor_custom.split('\n')
            ]

        if len(flowcharts) > 1:
            source.append(('', False, None))

        for flowchart in flowcharts:
            if flowchart.root.name != 'main':
                source.append((flowchart.get_function_declaration(), False, None))

        for i, flowchart in enumerate(flowcharts):
            source.append(('', False, None))
            source.extend(self._generate_code_(flowchart.root, set()))

        code_lines, break_points, nodes = map(list, zip(*source))

        for flowchart in flowcharts:
            for node in flowchart:
                node.lines = []

        for i, node in enumerate(nodes):  # type: ignore
            if node:
                cast(Node, node).lines.append(i + 1)  # type: ignore

        source_code = '\n'.join(cast(list[str], code_lines))
        break_point_definitions = '\n'.join(
            map(lambda e: f'break flowtutor.c:{e[0] + 2}',
                filter(lambda e: e[1],
                       enumerate(break_points))))

        return (source_code, break_point_definitions)
    
    def _generate_code_(self, node: Node, visited_nodes: set[Node]) -> Generator[tuple[str, bool, Optional[Node]], None, None]:
        visited_nodes.add(node)
        if isinstance(node, Template):
            loop_body: Any = sum([list(self._generate_code_(c.dst_node, visited_nodes)) for c in node.connections if c.src_ind == 1 and not c.dst_node in visited_nodes], [])
            yield from self.template_service.render(node, loop_body)
        elif isinstance(node, FunctionStart):
            parameters = ', '.join([str(p) for p in node.parameters])
            yield (f'{node.return_type} {node.name}({parameters}) {{', node.break_point, node)
        elif isinstance(node, FunctionEnd):
            yield (f'  return {node.return_value};', node.break_point, node)
            yield ('}', False, node)
        else:
            yield ('', False, None)
        for code in [self._generate_code_(c.dst_node, visited_nodes) for c in node.connections if c.src_ind == 0 and not c.dst_node in visited_nodes]:
            yield from code
