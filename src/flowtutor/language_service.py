from __future__ import annotations
from json import load as json_load
from typing import TYPE_CHECKING, Any, Optional, cast
from os import listdir, path
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
    '''A service that facilitates using languages defined in the templates folder.'''

    @inject
    def __init__(self,
                 utils_service: UtilService = Provide['utils_service'],
                 settings_service: SettingsService = Provide['settings_service']):
        self.utils_service = utils_service
        self.settings_service = settings_service
        self.is_initialized = False
        self.jinja_env: Optional[Environment] = None
        '''The currently initialized Jinja environment.'''
        self.template_cache: dict[str, JinjaTemplate] = {}
        '''A dict of Jinja tmeplates, to avoid regeneration on every call.'''

    def finish_init(self, flowchart: Flowchart) -> None:
        '''Finishes the initilization with the language selected for the flowchart.

        Parameters:
            flowchart (Flowchart): The flowchart the service gets initialized for.
        '''
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.utils_service.get_templates_path(flowchart.lang_data['lang_id'])),
            lstrip_blocks=True,
            trim_blocks=True)
        self.is_initialized = True

    def get_node_templates(self, flowchart: Flowchart) -> dict[str, Any]:
        '''Gets a dictionary of template data, with the template names as keys.

        Parameters:
            flowchart (Flowchart): The flowchart the nodes a loaded for.
        '''
        template_file_paths: list[str] = []
        templates_path = self.utils_service.get_templates_path(flowchart.lang_data['lang_id'])
        template_file_paths.extend(
            [path.join(templates_path, f) for f in listdir(templates_path) if f.endswith('template.json')])
        templates: dict[str, Any] = {}
        for template_file_path in template_file_paths:
            with open(template_file_path, 'r') as template_file:
                data = json_load(template_file)
                data['file_name'] = template_file.name
                templates[str(data['label'])] = data
        return templates

    def has_function_declarations(self, flowchart: Flowchart) -> bool:
        '''Checks if the language selected for the flowchart has function declarations.

        Parameters:
            flowchart (Flowchart): The flowchart to be checked.
        '''
        return 'function_declaration' in flowchart.lang_data

    def has_types(self, flowchart: Flowchart) -> bool:
        '''Checks if the language selected for the flowchart is typed.

        Parameters:
            flowchart (Flowchart): The flowchart to be checked.
        '''
        return 'types' in flowchart.lang_data

    def has_main_function(self, flowchart: Flowchart) -> bool:
        '''Checks if the language selected for the flowchart has a main function.

        Parameters:
            flowchart (Flowchart): The flowchart to be checked.
        '''
        return ('has_main_function' not in flowchart.lang_data or flowchart.lang_data['has_main_function'])

    def is_compiled(self, flowchart: Flowchart) -> bool:
        '''Checks if the language selected for the flowchart is compiled.

        Parameters:
            flowchart (Flowchart): The flowchart to be checked.
        '''
        return flowchart.lang_data['is_compiled'] is True if 'is_compiled' in flowchart.lang_data else False

    def get_languages(self) -> dict[str, Any]:
        '''Gets a dictionary of available languages. The key is the language identifier and the value is
        the language data.
        '''
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
                data = json_load(language_file)
                languages[str(data['lang_id'])] = data
        return languages

    def get_comment_specifier(self, flowchart: Flowchart) -> str:
        '''Gets the comment spcifier for the language of the flowchart.

        Parameters:
            flowchart (Flowchart): The flowchart to be checked.
        '''
        return str(flowchart.lang_data['comment_specifier'])\
            if 'comment_specifier' in flowchart.lang_data else '//'

    def render_template(self,
                        template: Template,
                        flowchart: Flowchart,
                        loop_body: list[tuple[str, Optional[Node]]],
                        if_branch: list[tuple[str, Optional[Node]]],
                        else_branch: list[tuple[str, Optional[Node]]]) -> list[tuple[str, Optional[Node]]]:
        '''Generates the source code for a template node.

        Parameters:
            template (Template): The template node.
            flowchart (Flowchart): The flowchart that contains the node.
            loop_body (list[tuple[str, Optional[Node]]]): A list of 'source code'-'Node' tuples, that have been
            pre-generated to be inserted into loops.
            if_branch (list[tuple[str, Optional[Node]]]): A list of 'source code'-'Node' tuples, that have been
            pre-generated to be inserted into decision branches.
            else_branch (list[tuple[str, Optional[Node]]]): A list of 'source code'-'Node' tuples, that have been
            pre-generated to be inserted into decision branches.
        '''
        template_body = template.body
        template.values['LOOP_BODY'] = '\n'.join([s1 for s1, _ in loop_body])
        template.values['IF_BRANCH'] = '\n'.join([s2 for s2, _ in if_branch])
        template.values['ELSE_BRANCH'] = '\n'.join([s3 for s3, _ in else_branch])
        rendered: list[tuple[str, Optional[Node]]] = []
        comment_specifier = self.get_comment_specifier(flowchart)
        if template.comment:
            rendered.append((f'{comment_specifier} {template.comment}', None))
        if template_body:
            rendered.append((self.render_line(template_body, template.values), template))
        else:
            path = Path(template.data['file_name'])
            filename_without_ext = path.stem.split('.')[0]
            try:
                unassigned_lines: list[tuple[str, Node | None]] = []
                unassigned_lines.extend(loop_body)
                unassigned_lines.extend(if_branch)
                unassigned_lines.extend(else_branch)
                unassigned_lines.reverse()
                assigned_nodes: set[Node] = set()
                rendered.extend(
                    [(l1, self.assign_node(l1, unassigned_lines, template, assigned_nodes))
                     for l1 in self.render_jinja_lines(filename_without_ext, template.values)])
            except TemplateNotFound:
                return [('', None)]
        if template.is_comment:
            return list(map(lambda r: (f'{comment_specifier} {r[0]}', r[1]), rendered))
        return rendered

    def render_function_declaration(self,
                                    flowchart: Flowchart,
                                    function_start: FunctionStart) -> list[tuple[str, Optional[Node]]]:
        '''Generates the source code for a function definition.

        Parameters:
            flowchart (Flowchart): The flowchart that contains the node.
            function_start (FunctionStart): The function start node
        '''
        rendered: list[tuple[str, Optional[Node]]] = []
        if 'function_declaration' in flowchart.lang_data:
            rendered.append((self.render_line(flowchart.lang_data['function_declaration'],
                                              {
                'FUN_NAME': function_start.name,
                'RETURN_TYPE': function_start.return_type,
                'PARAMETERS': function_start.parameters
            }), None))
        return rendered

    def render_imports(self, flowchart: Flowchart) -> list[tuple[str, Optional[Node]]]:
        '''Generates the source code for module imports.

        Parameters:
            flowchart (Flowchart): The flowchart object.
        '''
        rendered: list[tuple[str, Optional[Node]]] = []
        if 'import' in flowchart.lang_data:
            for imp in flowchart.imports:
                rendered.append(
                    (self.render_line(flowchart.lang_data['import'], {'IMPORT': imp}), None))
        return rendered

    def render_function(self,
                        function_start: FunctionStart,
                        function_end: FunctionEnd,
                        flowchart: Flowchart,
                        body: list[tuple[str, Optional[Node]]]) -> list[tuple[str, Optional[Node]]]:
        '''Generates the source code for a template node.

        Parameters:
            function_start (FunctionStart): The function start node.
            function_end (FunctionEnd): The function end node.
            flowchart (Flowchart): The flowchart that contains the node.
            body (list[tuple[str, Optional[Node]]]): A list of 'source code'-'Node' tuples, that have been
            pre-generated to be inserted into function bodies.
        '''
        values = {
            'FUN_NAME': function_start.name,
            'PARAMETERS': function_start.parameters,
            'BODY': '\n'.join([s1 for s1, _ in body]),
            'RETURN_TYPE': function_start.return_type,
            'RETURN_VALUE': function_end.return_value
        }
        rendered: list[tuple[str, Optional[Node]]] = []
        comment_specifier = self.get_comment_specifier(flowchart)
        if function_start.comment:
            rendered.append((f'{comment_specifier} {function_start.comment}', None))
        try:
            unassigned_lines = body.copy()
            unassigned_lines.reverse()
            assigned_nodes: set[Node] = set()
            tmp = [(l1, self.assign_node(l1, unassigned_lines, function_start, assigned_nodes))
                   for l1 in self.render_jinja_lines('function', values)]
            unassigned_lines = list(filter(lambda x: not x[1], tmp))
            if unassigned_lines:
                tmp[tmp.index(unassigned_lines[-1])] = unassigned_lines[-1][0], function_end
            rendered.extend(tmp)

        except TemplateNotFound:
            return [('', None)]
        return rendered

    def render_line(self, jinja_template_string: str, values: dict[str, Any]) -> str:
        '''Generates a single source code line from a Jinja template line.

        Parameters:
            jinja_template_string (str): The jinja template line.
            values (dict[str, Any]): A dictionary with variable assignemnts substituted in the template.
        '''
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
        '''Generates a source code block from a Jinja template.

        Parameters:
            template_file_name (str): The jinja template file name.
            values (dict[str, Any]): A dictionary with variable assignemnts substituted in the template.
        '''
        if self.jinja_env:
            return self.jinja_env.get_template(f'{template_file_name}.jinja').render(values).splitlines()
        else:
            return []

    def assign_node(self,
                    line: str,
                    unassigned_lines: list[tuple[str, Optional[Node]]],
                    default_node: Node,
                    assigned_nodes: set[Node]) -> Optional[Node]:
        '''Assigns a source code line to a node.

        Parameters:
            line (str): The line to assign.
            unassigned_lines (list[tuple[str, Optional[Node]]]): A list of tuple of source code lines and Nodes
            to be assigned.
            default_node (Node): The node that gets assigned if no other node fits.
            assigned_nodes (set[Node]): A set of assigned nodes, to avoid reassignment.
        '''
        if unassigned_lines and unassigned_lines[-1][0].strip() == line.strip():
            node = unassigned_lines.pop()[1]
        else:
            node = default_node
        if not node or node in assigned_nodes:
            return None
        assigned_nodes.add(node)
        return node

    def get_data_types(self, flowchart: Optional[Flowchart] = None) -> list[str]:
        '''Get a list of available data types in the flowcharts.

        Includes user defined types and structs.

        Parameters:
            flowchart (Flowchart): The flowchart to be checked.
        '''
        struct_defintions = list(map(lambda s: f'{s.name}_t', flowchart.struct_definitions)) if flowchart else []
        type_defintions = list(map(lambda s: s.name, flowchart.type_definitions)) if flowchart else []
        lang_types: list[str] = flowchart.lang_data['types'] if flowchart and 'types' in flowchart.lang_data else []
        return lang_types + type_defintions + struct_defintions

    def get_node_shape_data(self, node_type: str) -> tuple[list[list[tuple[float, float]]], tuple[int, int, int]]:
        '''Gets shape data corresponding to a node type.

        Parameters:
            node_type (str): The node type to get shape data for.
        '''
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
        '''Get a list of modules, that get imported by default on new programs.

        Parameters:
            flowchart (Flowchart): The flowchart to be checked.
        '''
        standard_headers: list[str] = flowchart.lang_data['standard_imports']\
            if 'standard_imports' in flowchart.lang_data else []
        return standard_headers
