from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional, cast
from os import listdir, path
import json
from pathlib import Path
from dependency_injector.wiring import Provide, inject
from jinja2 import Environment, FileSystemLoader, TemplateNotFound, Template as JinjaTemplate

if TYPE_CHECKING:
    from flowtutor.flowchart.functionstart import FunctionStart
    from flowtutor.flowchart.functionend import FunctionEnd
    from flowtutor.settings_service import SettingsService
    from flowtutor.util_service import UtilService
    from flowtutor.flowchart.node import Node
    from flowtutor.flowchart.template import Template
    from flowtutor.flowchart.flowchart import Flowchart


class LanguageService:

    @inject
    def __init__(self,
                 utils_service: UtilService = Provide['utils_service'],
                 settings_service: SettingsService = Provide['settings_service']):
        self.utils_service = utils_service
        self.settings_service = settings_service
        self.is_initialized = False
        self.jinja_env: Optional[Environment] = None
        self.template_cache: dict[str, JinjaTemplate] = {}

    def finish_init(self, flowchart: Flowchart) -> None:
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.utils_service.get_templates_path(flowchart.lang_data['lang_id'])),
            lstrip_blocks=True,
            trim_blocks=True)
        self.is_initialized = True

    def get_node_templates(self, flowchart: Flowchart) -> dict[str, Any]:
        template_file_paths: list[str] = []
        templates_path = self.utils_service.get_templates_path(flowchart.lang_data['lang_id'])
        template_file_paths.extend(
            [path.join(templates_path, f) for f in listdir(templates_path) if f.endswith('template.json')])
        templates: dict[str, Any] = {}
        for template_file_path in template_file_paths:
            with open(template_file_path, 'r') as template_file:
                data = json.load(template_file)
                data['file_name'] = template_file.name
                templates[str(data['label'])] = data
        return templates

    def get_languages(self) -> dict[str, Any]:
        language_paths: list[str] = []
        templates_path = self.utils_service.get_templates_path()
        language_paths.extend(
            [path.join(templates_path, f) for f in listdir(templates_path)])

        languages: dict[str, Any] = {}
        for language_path in language_paths:
            language_file_path = path.join(language_path, 'language.json')
            if not path.exists(language_file_path):
                continue
            with open(language_file_path, 'r') as language_file:
                data = json.load(language_file)
                languages[str(data['lang_id'])] = data
        return languages

    def render_template(self,
                        template: Template,
                        loop_body: list[tuple[str, Optional[Node]]],
                        if_branch: list[tuple[str, Optional[Node]]],
                        else_branch: list[tuple[str, Optional[Node]]]) -> list[tuple[str, Optional[Node]]]:
        template_body = template.body
        template.values['LOOP_BODY'] = '\n'.join([s1 for s1, _ in loop_body])
        template.values['IF_BRANCH'] = '\n'.join([s2 for s2, _ in if_branch])
        template.values['ELSE_BRANCH'] = '\n'.join([s3 for s3, _ in else_branch])
        rendered: list[tuple[str, Optional[Node]]] = []
        if template.comment:
            rendered.append((f'// {template.comment}', None))
        if template_body:
            rendered.append((self.render_line(template_body, template.values), template))
        else:
            path = Path(template.data['file_name'])
            filename_without_ext = path.stem.split('.')[0]
            try:
                unassigned_lines = loop_body.copy()
                unassigned_lines.reverse()
                assigned_nodes: set[Node] = set()
                rendered.extend(
                    [(l1, self.assign_node(l1, unassigned_lines, template, assigned_nodes))
                     for l1 in self.render_jinja_lines(filename_without_ext, template.values)])

            except TemplateNotFound:
                return [('', None)]
        return rendered

    def render_imports(self, flowchart: Flowchart) -> list[tuple[str, Optional[Node]]]:
        rendered: list[tuple[str, Optional[Node]]] = []
        if 'import' in flowchart.lang_data:
            for imp in flowchart.includes:
                rendered.append(
                    (self.render_line(flowchart.lang_data['import'], {'IMPORT': imp}), None))
        return rendered

    def render_function(self,
                        function_start: FunctionStart,
                        function_end: FunctionEnd,
                        body: list[tuple[str, Optional[Node]]]) -> list[tuple[str, Optional[Node]]]:
        values = {
            'FUN_NAME': function_start.name,
            'PARAMETERS': function_start.parameters,
            'BODY': '\n'.join([s1 for s1, _ in body]),
            'RETURN_TYPE': function_start.return_type,
            'RETURN_VALUE': function_end.return_value
        }
        rendered: list[tuple[str, Optional[Node]]] = []
        if function_start.comment:
            rendered.append((f'// {function_start.comment}', None))
        try:
            unassigned_lines = body.copy()
            unassigned_lines.reverse()
            assigned_nodes: set[Node] = set()
            rendered.extend(
                [(l1, self.assign_node(l1, unassigned_lines, function_start, assigned_nodes))
                 for l1 in self.render_jinja_lines('function', values)])
        except TemplateNotFound:
            return [('', None)]
        return rendered

    def render_line(self, jinja_template_string: str, values: dict[str, Any]) -> str:
        if self.jinja_env:
            if jinja_template_string in self.template_cache:
                jinja_template = self.template_cache[jinja_template_string]
            else:
                jinja_template = self.jinja_env.from_string(jinja_template_string)
                self.template_cache[jinja_template_string] = jinja_template
            return jinja_template.render(values)
        else:
            return ''

    def render_jinja_lines(self, template_file_name: str, values: dict[str, Any]) -> list[str]:
        if self.jinja_env:
            return self.jinja_env.get_template(f'{template_file_name}.jinja').render(values).splitlines()
        else:
            return []

    def assign_node(self,
                    line: str,
                    unassigned_lines: list[tuple[str, Optional[Node]]],
                    default_node: Node,
                    assigned_nodes: set[Node]) -> Optional[Node]:
        if unassigned_lines and unassigned_lines[-1][0].strip() == line.strip():
            node = unassigned_lines.pop()[1]
        else:
            node = default_node
        if not node or node in assigned_nodes:
            return None
        assigned_nodes.add(node)
        return node

    def get_data_types(self, flowchart: Optional[Flowchart] = None) -> list[str]:
        struct_defintions = list(map(lambda s: f'{s.name}_t', flowchart.struct_definitions)) if flowchart else []
        type_defintions = list(map(lambda s: s.name, flowchart.type_definitions)) if flowchart else []
        lang_types: list[str] = flowchart.lang_data['types'] if flowchart and 'types' in flowchart.lang_data else []
        return lang_types + type_defintions + struct_defintions

    def get_node_shape_data(self, node_type: str) -> tuple[list[list[tuple[float, float]]], tuple[int, int, int]]:
        return cast(tuple[list[list[tuple[float, float]]], tuple[int, int, int]], {
            'data': ([[(20.0, 0.0),
                      (150.0, 0.0),
                      (130.0, 75.0),
                      (0.0, 75.0),
                      (20.0, 0.0)]],
                     (147, 171, 255)),
            'data_internal': ([[(0.0, 0.0),
                                (150, 0),
                                (150, 75),
                                (0, 75),
                                (0, 0)],
                               [(0, 10),
                                (150, 10)],
                               [(10, 0),
                                (10, 75)]],
                              (255, 255, 170)),
            'process': ([[(0.0, 0.0),
                         (150, 0),
                         (150, 75),
                         (0, 75),
                         (0, 0)]],
                        (255, 255, 170)),
            'predefined_process': ([[(0.0, 0.0),
                                    (150, 0),
                                    (150, 75),
                                    (0, 75),
                                    (0, 0)],
                                    [(10, 0),
                                    (10, 75)],
                                    [(140, 75),
                                    (140, 0)]],
                                   (255, 255, 170)),
            'preparation': ([[(0.0, 37.5),
                             (20, 75),
                             (130, 75),
                             (150, 37.5),
                             (130, 0),
                             (20, 0),
                             (0, 37.5)]],
                            (255, 208, 147)),
            'decision': ([[(75.0, 0.0),
                          (0, 50),
                          (75, 100),
                          (150, 50),
                          (75, 0)]],
                         (255, 170, 170)),
            'terminator': ([[(0.0, 37.5),
                            (1, 30),
                            (3, 23),
                            (6, 17),
                            (11, 11),
                            (17, 6),
                            (23, 3),
                            (30, 1),
                            (37.5, 0),
                            (112.5, 0),
                            (120, 1),
                            (127, 3),
                            (133, 6),
                            (139, 11),
                            (144, 17),
                            (147, 23),
                            (149, 30),
                            (150, 37.5),
                            (149, 45),
                            (147, 52),
                            (144, 58),
                            (139, 64),
                            (133, 69),
                            (127, 72),
                            (120, 74),
                            (112.5, 75),
                            (37.5, 75),
                            (30, 74),
                            (23, 72),
                            (17, 69),
                            (11, 64),
                            (6, 58),
                            (3, 52),
                            (1, 45),
                            (0, 37.5)]],
                           (200, 170, 255))
        }[node_type])

    def get_standard_headers(self, flowchart: Flowchart) -> list[str]:
        standard_headers: list[str] = flowchart.lang_data['standard_imports']\
            if 'standard_imports' in flowchart.lang_data else []
        return standard_headers