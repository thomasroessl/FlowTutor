from typing import TYPE_CHECKING, Optional
from pathlib import Path
from dependency_injector.wiring import Provide, inject
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from flowtutor.util_service import UtilService
from flowtutor.flowchart.node import Node
from flowtutor.flowchart.template import Template


class TemplateService:

    @inject
    def __init__(self, utils_service: UtilService = Provide['utils_service']) -> None:
        self.utils_service = utils_service
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.utils_service.get_templates_path()),
            lstrip_blocks=True,
            trim_blocks=True)

    def render(self, template: Template, loop_body: list[tuple[str, Optional[Node]]], if_branch: list[tuple[str, Optional[Node]]], else_branch: list[tuple[str, Optional[Node]]]) -> list[tuple[str, Optional[Node]]]:
        template_body = template.body
        template.values['LOOP_BODY'] = '\n'.join([l for l, _ in loop_body])
        template.values['IF_BRANCH'] = '\n'.join([l for l, _ in if_branch])
        template.values['ELSE_BRANCH'] = '\n'.join([l for l, _ in else_branch])
        rendered: list[tuple[str, Optional[Node]]] = []
        if template.comment:
            rendered.append((f'  // {template.comment}', None))
        if template_body:
            rendered.append(('  ' + self.render_line(template_body, template.values), template))
        else:
            path = Path(template.data['file_name'])
            filename_without_ext = path.stem.split('.')[0]
            try:
                unassigned_lines = loop_body.copy()
                unassigned_lines.reverse()
                assigned_nodes: set[Node] = set()
                rendered.extend(
                    [('  ' + l, self.assign_node(l, unassigned_lines, template, assigned_nodes)) for l in self.render_jinja_lines(filename_without_ext, template.values)])

            except TemplateNotFound:
                return [('', None)]
        return rendered

    def render_line(self, jinja_template: str, values: dict[str, str]) -> str:
        return self.jinja_env.from_string(jinja_template).render(values)

    def render_jinja_lines(self, template_file_name: str, values: dict[str, str]) -> list[str]:
        return self.jinja_env.get_template(f'{template_file_name}.jinja').render(values).splitlines()

    def assign_node(self, line: str, unassigned_lines: list[tuple[str, Optional[Node]]], default_node: Node, assigned_nodes: set[Node]) -> Optional[Node]:
        if unassigned_lines and unassigned_lines[-1][0].strip() == line.strip():
            node = unassigned_lines.pop()[1]
        else:
            node = default_node
        if not node or node in assigned_nodes:
            return None
        assigned_nodes.add(node)
        return node
