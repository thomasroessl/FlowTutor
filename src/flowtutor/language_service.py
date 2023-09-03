from typing import Any, Optional
from os import listdir, path
import json
from pathlib import Path
from dependency_injector.wiring import Provide, inject
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from flowtutor.flowchart.functionend import FunctionEnd
from flowtutor.flowchart.functionstart import FunctionStart

from flowtutor.settings_service import SettingsService
from flowtutor.util_service import UtilService
from flowtutor.flowchart.node import Node
from flowtutor.flowchart.template import Template


class LanguageService:

    @inject
    def __init__(self,
                 utils_service: UtilService = Provide['utils_service'],
                 settings_service: SettingsService = Provide['settings_service']):
        self.utils_service = utils_service
        self.settings_service = settings_service
        self.is_initialized = False
        self.jinja_env: Optional[Environment] = None

    @property
    def lang_id(self) -> str:
        return self.settings_service.get_setting('lang_id')

    def finish_init(self) -> None:
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.utils_service.get_templates_path(self.lang_id)),
            lstrip_blocks=True,
            trim_blocks=True)
        self.is_initialized = True

    def get_node_templates(self) -> dict[str, Any]:
        template_file_paths: list[str] = []
        templates_path = self.utils_service.get_templates_path(self.lang_id)
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

    def render_line(self, jinja_template: str, values: dict[str, Any]) -> str:
        if self.jinja_env:
            return self.jinja_env.from_string(jinja_template).render(values)
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
