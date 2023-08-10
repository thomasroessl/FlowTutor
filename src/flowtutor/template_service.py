from pathlib import Path
from flowtutor.util_service import UtilService
from dependency_injector.wiring import Provide, inject
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from flowtutor.flowchart.template import Template


class TemplateService:

    @inject
    def __init__(self, utils_service: UtilService = Provide['utils_service']) -> None:
        self.utils_service = utils_service
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.utils_service.get_templates_path()),
            lstrip_blocks=True,
            trim_blocks=True)

    def render(self, template: Template) -> str:
        template_body = template.body
        if not template_body:
            path = Path(template.data['file_name'])
            filename_without_ext = path.stem.split('.')[0]
            try:
                return self.jinja_env.get_template(f'{filename_without_ext}.jinja').render(template.values)
            except TemplateNotFound:
                return ''
        elif isinstance(template_body, str):
            return self.jinja_env.from_string(template_body).render(template.values)
        else:
            return '\n'.join(map(lambda t: self.jinja_env.from_string(t).render(template.values), template_body))