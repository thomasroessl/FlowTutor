from typing import Any
from os import walk, path
import json
from dependency_injector.wiring import Provide, inject

from flowtutor.util_service import UtilService


class LanguageService:

    @inject
    def __init__(self,
                 utils_service: UtilService = Provide['utils_service']):
        self.utils_service = utils_service

    def get_node_templates(self) -> dict[str, Any]:
        template_file_paths: list[str] = []
        for (dirpath, _, file_names) in walk(self.utils_service.get_templates_path(), False):
            print(dirpath, file_names)
            template_file_paths.extend([path.join(dirpath, f) for f in file_names])
        templates: dict[str, Any] = {}
        for template_file_path in template_file_paths:
            if not template_file_path.endswith('template.json'):
                continue
            with open(template_file_path, 'r') as template_file:
                data = json.load(template_file)
                data['file_name'] = template_file.name
                templates[str(data['label'])] = data
        return templates
