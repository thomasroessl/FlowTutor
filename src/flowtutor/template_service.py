from typing import Optional
from pathlib import Path
from flowtutor.util_service import UtilService
from dependency_injector.wiring import Provide, inject
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from flowtutor.flowchart.template import Template
from flowtutor.flowchart.node import Node


class TemplateService:

    @inject
    def __init__(self, utils_service: UtilService = Provide['utils_service']) -> None:
        self.utils_service = utils_service
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.utils_service.get_templates_path()),
            lstrip_blocks=True,
            trim_blocks=True)

    def render(self, template: Template, loop_body: list[tuple[str, bool, Optional[Node]]]) -> list[tuple[str, bool, Optional[Node]]]:
        template_body = template.body
        template.values['LOOP_BODY'] = '\n'.join([l for l, _, _ in loop_body])
        if not template_body:
            path = Path(template.data['file_name'])
            filename_without_ext = path.stem.split('.')[0]
            try:
                return [('  ' + l, True, template) for l in self.jinja_env.get_template(f'{filename_without_ext}.jinja').render(template.values).splitlines()]
            except TemplateNotFound:
                return [('', False, None)]
        elif isinstance(template_body, str):
            return [('  ' + self.jinja_env.from_string(template_body).render(template.values), True, template)]
        else:
            return list(map(lambda t: ('  ' + self.jinja_env.from_string(t).render(template.values), True, template), template_body))
