from typing import Optional, Any, Type
from os import walk, path
import json
from dependency_injector.wiring import Provide, inject

from flowtutor.flowchart.assignment import Assignment
from flowtutor.flowchart.call import Call
from flowtutor.flowchart.declarations import Declarations
from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.forloop import ForLoop
from flowtutor.flowchart.whileloop import WhileLoop
from flowtutor.flowchart.dowhileloop import DoWhileLoop
from flowtutor.flowchart.input import Input
from flowtutor.flowchart.output import Output
from flowtutor.flowchart.snippet import Snippet
from flowtutor.flowchart.template import Template
from flowtutor.util_service import UtilService
from flowtutor.flowchart.node import Node


class NodesService:

    @inject
    def __init__(self,
                 utils_service: UtilService = Provide['utils_service']):
        self.utils_service = utils_service

    def get_node_types(self) -> list[tuple[str, Type[Node], Optional[Any]]]:
        return [
            ('Assignment', Assignment, None),
            ('Call', Call, None),
            ('Declaration', Declarations, None),
            ('Conditional', Conditional, None),
            ('For Loop', ForLoop, None),
            ('While Loop', WhileLoop, None),
            ('Do-While Loop', DoWhileLoop, None),
            ('Input', Input, None),
            ('Output', Output, None),
            ('Code Snippet', Snippet, None)
        ] + self.get_node_templates()

    def get_node_templates(self) -> list[tuple[str, Type[Node], Any]]:
        template_file_paths: list[str] = []
        for (dirpath, _, file_names) in walk(self.utils_service.get_templates_path()):
            template_file_paths.extend([path.join(dirpath, f) for f in file_names])
        templates: list[tuple[str, Type[Node], Any]] = []
        for template_file_path in template_file_paths:
            with open(template_file_path, 'r') as template_file:
                data = json.load(template_file)
                templates.append((str(data['label']), Template, data))
        return templates
