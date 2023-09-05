from typing import Any
from unittest.mock import patch
import pytest

from flowtutor.codegenerator import CodeGenerator
from flowtutor.containers import Container
from flowtutor.flowchart.flowchart import Flowchart
from flowtutor.flowchart.struct_definition import StructDefinition
from flowtutor.flowchart.struct_member import StructMember
from flowtutor.flowchart.type_definition import TypeDefinition
from flowtutor.flowchart.parameter import Parameter
from flowtutor.flowchart.template import Template

from flowtutor.flowchart.node import dpg as node_dpg
from flowtutor.language_service import LanguageService

C_TYPES = [
    'char',
    'unsigned char',
    'short',
    'unsigned short',
    'int',
    'unsigned int',
    'long',
    'unsigned long',
    'float',
    'double',
    'long double'
]

C_FORMAT_SPECIFIERS = [
    [
        '%c',
        '%c',
        '%hd',
        '%hu',
        '%d',
        '%u',
        '%ld',
        '%lu',
        '%f',
        '%lf',
        '%Lf'
    ]
]


@patch.object(node_dpg, 'get_text_size', lambda _: (0, 0))
class TestCodeGenerator:

    @pytest.fixture(scope='session')
    def code_generator(self) -> CodeGenerator:
        container = Container()
        container.init_resources()
        container.wire(modules=[
            'flowtutor.codegenerator',
            'flowtutor.language_service',
            'flowtutor.flowchart.functionstart',
            'flowtutor.flowchart.functionend'])
        code_generator = CodeGenerator()
        flowchart = Flowchart('main', {
            'lang_id': 'c'
        })
        code_generator.language_service.finish_init(flowchart)
        return code_generator

    @pytest.fixture(scope='session')
    def nodes(self) -> dict[str, Any]:
        container = Container()
        container.init_resources()
        container.wire(modules=[
            'flowtutor.language_service',
            'flowtutor.flowchart.template',
            'flowtutor.flowchart.functionstart',
            'flowtutor.flowchart.functionend'])
        language_service = LanguageService()
        flowchart = Flowchart('main', {
            'lang_id': 'c'
        })
        language_service.finish_init(flowchart)
        return language_service.get_node_templates(flowchart)

    @pytest.fixture()
    def flowchart(self) -> Flowchart:
        flowchart = Flowchart('main', {
            'lang_id': 'c',
            'import': '#include <{{IMPORT}}>',
            'function_declaration': '{{RETURN_TYPE}} {{FUN_NAME}}({% for p in PARAMETERS %}{{p.type}} {{p.name}}{{ \",'
            ' \" if not loop.last else \"\" }}{% endfor %});'
        })
        flowchart.imports.append('stdio.h')
        return flowchart

    def test_code_from_empty_flowchart(self, flowchart: Flowchart, code_generator: CodeGenerator):
        code, _ = code_generator.generate_code([flowchart])
        print(code)
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            '  return 0;',
            '}'])
        print(expected)
        assert code == expected, 'An empty flowchart should produce a main function, which returns 0.'

    def test_code_from_imports(self, flowchart: Flowchart, code_generator: CodeGenerator):
        flowchart.imports.append('test1.h')
        flowchart.imports.append('test2.h')
        code, _ = code_generator.generate_code([flowchart])
        print(code)
        expected = '\n'.join([
            '#include <stdio.h>',
            '#include <test1.h>',
            '#include <test2.h>',
            '',
            'int main() {',
            '  return 0;',
            '}'])
        print(expected)
        assert code == expected, 'Selected headers should be included in the source file.'

    @pytest.mark.parametrize('data_type', C_TYPES)
    def test_code_from_declaration(self,
                                   data_type: str,
                                   flowchart: Flowchart,
                                   code_generator: CodeGenerator,
                                   nodes: dict[str, Any]):
        declaration = Template(nodes['Declaration'])
        declaration.values['VAR_NAME'] = 'x'
        declaration.values['VAR_TYPE'] = data_type
        declaration.values['VAR_VALUE'] = '3'
        flowchart.add_node(flowchart.root, declaration)
        code, _ = code_generator.generate_code([flowchart])
        print('---------------------OUTPUT:---------------------------------')
        print(code)
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            f'  {data_type} x = 3;',
            '  return 0;',
            '}'])
        print('---------------------EXPECTED:-------------------------------')
        print(expected)
        assert code == expected, 'Declaration with value.'

    @pytest.mark.parametrize('data_type', C_TYPES)
    def test_code_from_static_declaration(self,
                                          data_type: str,
                                          flowchart: Flowchart,
                                          code_generator: CodeGenerator,
                                          nodes: dict[str, Any]):
        declaration = Template(nodes['Declaration'])
        declaration.values['VAR_NAME'] = 'x'
        declaration.values['IS_STATIC'] = True
        declaration.values['VAR_TYPE'] = data_type
        declaration.values['VAR_VALUE'] = '3'
        flowchart.add_node(flowchart.root, declaration)
        code, _ = code_generator.generate_code([flowchart])
        print(code)
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            f'  static {data_type} x = 3;',
            '  return 0;',
            '}'])
        print(expected)
        assert code == expected, 'Static declaration with initialization.'

    @pytest.mark.parametrize('data_type', C_TYPES)
    def test_code_from_pointer_declaration(self,
                                           data_type: str,
                                           flowchart: Flowchart,
                                           code_generator: CodeGenerator,
                                           nodes: dict[str, Any]):
        declaration = Template(nodes['Declaration'])
        declaration.values['VAR_NAME'] = 'x'
        declaration.values['IS_POINTER'] = True
        declaration.values['VAR_TYPE'] = data_type
        flowchart.add_node(flowchart.root, declaration)
        code, _ = code_generator.generate_code([flowchart])
        print(code)
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            f'  {data_type} *x;',
            '  return 0;',
            '}'])
        print(expected)
        assert code == expected, 'Pointer declaration.'

    def test_code_from_assignment(self,
                                  flowchart: Flowchart,
                                  code_generator: CodeGenerator,
                                  nodes: dict[str, Any]):
        assignment = Template(nodes['Assignment'])
        assignment.values['VAR_NAME'] = 'x'
        assignment.values['VAR_VALUE'] = '3'
        flowchart.add_node(flowchart.root, assignment)
        code, _ = code_generator.generate_code([flowchart])
        print(code)
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            '  x = 3;',
            '  return 0;',
            '}'])
        print(expected)
        assert code == expected, 'Assignment.'

    def test_code_from_assignment_with_comment(self,
                                               flowchart: Flowchart,
                                               code_generator: CodeGenerator,
                                               nodes: dict[str, Any]):
        assignment = Template(nodes['Assignment'])
        assignment.values['VAR_NAME'] = 'x'
        assignment.values['VAR_VALUE'] = '3'
        assignment.comment = 'This is a comment'
        flowchart.add_node(flowchart.root, assignment)
        code, _ = code_generator.generate_code([flowchart])
        print(code)
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            '  // This is a comment',
            '  x = 3;',
            '  return 0;',
            '}'])
        print(expected)
        assert code == expected, 'Assignment.'

    def test_code_from_array_assignment(self,
                                        flowchart: Flowchart,
                                        code_generator: CodeGenerator,
                                        nodes: dict[str, Any]):
        assignment = Template(nodes['Assignment'])
        assignment.values['VAR_NAME'] = 'x[0]'
        assignment.values['VAR_VALUE'] = '3'
        flowchart.add_node(flowchart.root, assignment)
        code, _ = code_generator.generate_code([flowchart])
        print(code)
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            '  x[0] = 3;',
            '  return 0;',
            '}'])
        print(expected)
        assert code == expected, 'Assignment.'

    def test_code_from_conditional(self,
                                   flowchart: Flowchart,
                                   code_generator: CodeGenerator,
                                   nodes: dict[str, Any]):
        conditional = Template(nodes['Conditional'])
        conditional.values['CONDITION'] = 'x > 5'
        flowchart.add_node(flowchart.root, conditional)
        code, _ = code_generator.generate_code([flowchart])
        print(code)
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            '  if(x > 5) {',
            '  }',
            '  return 0;',
            '}'])
        print(expected)
        assert code == expected, 'Conditional.'

    def test_code_from_conditional_with_one_branch(self,
                                                   flowchart: Flowchart,
                                                   code_generator: CodeGenerator,
                                                   nodes: dict[str, Any]):
        conditional = Template(nodes['Conditional'])
        conditional.values['CONDITION'] = 'x > 5'
        flowchart.add_node(flowchart.root, conditional)

        assignment = Template(nodes['Assignment'])
        assignment.values['VAR_NAME'] = 'x'
        assignment.values['VAR_VALUE'] = '3'
        flowchart.add_node(conditional, assignment, 1)

        code, _ = code_generator.generate_code([flowchart])
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            '  if(x > 5) {',
            '    x = 3;',
            '  }',
            '  return 0;',
            '}'])
        print(code)
        print(expected)
        assert code == expected, 'Conditional.'

    def test_code_from_conditional_with_two_branches(self,
                                                     flowchart: Flowchart,
                                                     code_generator: CodeGenerator,
                                                     nodes: dict[str, Any]):
        conditional = Template(nodes['Conditional'])
        conditional.values['CONDITION'] = 'x > 5'
        flowchart.add_node(flowchart.root, conditional)

        assignment1 = Template(nodes['Assignment'])
        assignment1.values['VAR_NAME'] = 'x'
        assignment1.values['VAR_VALUE'] = '3'
        flowchart.add_node(conditional, assignment1, 1)

        assignment2 = Template(nodes['Assignment'])
        assignment2.values['VAR_NAME'] = 'x'
        assignment2.values['VAR_VALUE'] = '5'
        flowchart.add_node(conditional, assignment2, 0)

        code, _ = code_generator.generate_code([flowchart])
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            '  if(x > 5) {',
            '    x = 3;',
            '  } else {',
            '    x = 5;',
            '  }',
            '  return 0;',
            '}'])
        print(code)
        print(expected)
        assert code == expected, 'Conditional.'

    def test_code_from_whileloop(self, flowchart: Flowchart, code_generator: CodeGenerator, nodes: dict[str, Any]):
        loop = Template(nodes['While loop'])
        loop.values['CONDITION'] = 'x > 5'
        flowchart.add_node(flowchart.root, loop)

        assignment = Template(nodes['Assignment'])
        assignment.values['VAR_NAME'] = 'x'
        assignment.values['VAR_VALUE'] = '3'
        flowchart.add_node(loop, assignment, 1)

        code, _ = code_generator.generate_code([flowchart])
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            '  while(x > 5) {',
            '    x = 3;',
            '  }',
            '  return 0;',
            '}'])
        print(code)
        print(expected)
        assert code == expected, 'While-Loop.'

    def test_code_from_do_while_loop(self, flowchart: Flowchart, code_generator: CodeGenerator, nodes: dict[str, Any]):
        loop = Template(nodes['Do-While loop'])
        loop.values['CONDITION'] = 'x > 5'
        flowchart.add_node(flowchart.root, loop)

        assignment = Template(nodes['Assignment'])
        assignment.values['VAR_NAME'] = 'x'
        assignment.values['VAR_VALUE'] = '3'
        flowchart.add_node(loop, assignment, 1)

        code, _ = code_generator.generate_code([flowchart])
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            '  do {',
            '    x = 3;',
            '  } while(x > 5);',
            '  return 0;',
            '}'])
        print(code)
        print(expected)
        assert code == expected, 'While-Loop.'

    def test_code_from_forloop(self, flowchart: Flowchart, code_generator: CodeGenerator, nodes: dict[str, Any]):
        loop = Template(nodes['For loop'])
        loop.values['CONDITION'] = 'i < 10'
        flowchart.add_node(flowchart.root, loop)

        assignment = Template(nodes['Assignment'])
        assignment.values['VAR_NAME'] = 'x'
        assignment.values['VAR_VALUE'] = 'x + 3'
        flowchart.add_node(loop, assignment, 1)

        code, _ = code_generator.generate_code([flowchart])
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            '  for(int i = 0; i < 10; i++) {',
            '    x = x + 3;',
            '  }',
            '  return 0;',
            '}'])
        print(code)
        print(expected)
        assert code == expected, 'For-Loop.'

    @pytest.mark.parametrize('data_type_format', list(zip(C_TYPES, C_FORMAT_SPECIFIERS)))
    def test_code_from_input(self,
                             data_type_format: tuple[str, str],
                             flowchart: Flowchart,
                             code_generator: CodeGenerator,
                             nodes: dict[str, Any]):
        data_type, format_specifier = data_type_format

        declaration = Template(nodes['Declaration'])
        declaration.values['VAR_NAME'] = 'x'
        declaration.values['VAR_TYPE'] = data_type

        input = Template(nodes['Input'])
        input.values['VAR_NAME'] = 'x'
        input.values['TEMPLATE_SPECIFIER'] = format_specifier

        flowchart.add_node(flowchart.root, declaration)
        flowchart.add_node(declaration, input)

        code, _ = code_generator.generate_code([flowchart])
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            f'  {data_type} x;',
            f'  scanf("{format_specifier}", &x);',
            '  return 0;',
            '}'])
        print(code)
        print(expected)
        assert code == expected, 'Input.'

    def test_code_from_output(self, flowchart: Flowchart, code_generator: CodeGenerator, nodes: dict[str, Any]):
        output = Template(nodes['Output'])
        output.values['TEMPLATE'] = 'This is the output.'

        flowchart.add_node(flowchart.root, output)

        code, _ = code_generator.generate_code([flowchart])
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            '  printf("This is the output.");',
            '  return 0;',
            '}'])
        print(code)
        print(expected)
        assert code == expected, 'Output.'

    def test_code_from_snippet(self, flowchart: Flowchart, code_generator: CodeGenerator, nodes: dict[str, Any]):
        snippet = Template(nodes['Snippet'])
        snippet.values['CODE'] = 'printf("Test Code line 1");\nprintf("Test Code line 2");'

        flowchart.add_node(flowchart.root, snippet)

        code, _ = code_generator.generate_code([flowchart])
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            '  printf("Test Code line 1");',
            '  printf("Test Code line 2");',
            '  return 0;',
            '}'])
        print(code)
        print(expected)
        assert code == expected, 'Snippet.'

    def test_code_from_output_with_arguments(self,
                                             flowchart: Flowchart,
                                             code_generator: CodeGenerator,
                                             nodes: dict[str, Any]):
        output = Template(nodes['Output'])
        output.values['TEMPLATE'] = 'This is the output: %d'
        output.values['ARGUMENTS'] = '5'

        flowchart.add_node(flowchart.root, output)

        code, _ = code_generator.generate_code([flowchart])
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            '  printf("This is the output: %d", 5);',
            '  return 0;',
            '}'])
        print(code)
        print(expected)
        assert code == expected, 'Output with arguments.'

    def test_code_from_multiple_empty_functions(self, flowchart: Flowchart, code_generator: CodeGenerator):
        flowchart2 = Flowchart('func1', flowchart.lang_data)

        flowchart3 = Flowchart('func2', flowchart.lang_data)

        code, _ = code_generator.generate_code([flowchart, flowchart2, flowchart3])
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'int func1();',
            'int func2();',
            '',
            'int main() {',
            '  return 0;',
            '}',
            '',
            'int func1() {',
            '  return 0;',
            '}',
            '',
            'int func2() {',
            '  return 0;',
            '}'
        ])
        print(code)
        print(expected)
        assert code == expected, 'Declaration of multiple empty functions.'

    def test_code_from_multiple_empty_functions_with_arguments(self,
                                                               flowchart: Flowchart,
                                                               code_generator: CodeGenerator):
        flowchart2 = Flowchart('func1', flowchart.lang_data)

        flowchart3 = Flowchart('func2', flowchart.lang_data)
        flowchart3.root.return_type = 'float'

        parameter1 = Parameter()
        parameter1.name = 'x'
        parameter1.type = 'int'
        parameter2 = Parameter()
        parameter2.name = 'y'
        parameter2.type = 'long'
        parameter3 = Parameter()
        parameter3.name = 'z'
        parameter3.type = 'unsigned int'
        flowchart2.root.parameters.append(parameter1)
        flowchart2.root.parameters.append(parameter2)
        flowchart3.root.parameters.append(parameter3)

        code, _ = code_generator.generate_code([flowchart, flowchart2, flowchart3])
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'int func1(int x, long y);',
            'float func2(unsigned int z);',
            '',
            'int main() {',
            '  return 0;',
            '}',
            '',
            'int func1(int x, long y) {',
            '  return 0;',
            '}',
            '',
            'float func2(unsigned int z) {',
            '  return 0;',
            '}'
        ])
        print(code)
        print(expected)
        assert code == expected, 'Declaration of multiple empty functions.'

    def test_code_from_typedef(self, flowchart: Flowchart, code_generator: CodeGenerator):
        type_definition1 = TypeDefinition()
        type_definition1.definition = 'char *'
        type_definition1.name = 'string'
        flowchart.type_definitions.append(type_definition1)
        type_definition2 = TypeDefinition()
        type_definition2.definition = 'int'
        type_definition2.name = 'testtype'
        flowchart.type_definitions.append(type_definition2)
        type_definition3 = TypeDefinition()
        type_definition3.definition = ' long   '
        type_definition3.name = 'testtype2'
        flowchart.type_definitions.append(type_definition3)
        code, _ = code_generator.generate_code([flowchart])
        print(code)
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'typedef char *string;',
            'typedef int testtype;',
            'typedef long testtype2;',
            '',
            'int main() {',
            '  return 0;',
            '}'])
        print(expected)
        assert code == expected, 'Type definitions should be included in the source file.'

    def test_code_from_struct(self, flowchart: Flowchart, code_generator: CodeGenerator):
        struct_definition = StructDefinition()
        struct_definition.members.clear()
        struct_definition.name = 'Test'
        struct_member1 = StructMember()
        struct_member1.name = 'x'
        struct_member1.type = 'int'
        struct_definition.members.append(struct_member1)
        struct_member2 = StructMember()
        struct_member2.name = 'y'
        struct_member2.type = 'long'
        struct_member2.is_pointer = True
        struct_definition.members.append(struct_member2)
        struct_member3 = StructMember()
        struct_member3.name = 'z'
        struct_member3.type = 'long'
        struct_member3.is_array = True
        struct_member3.array_size = '10'
        struct_definition.members.append(struct_member3)
        flowchart.struct_definitions.append(struct_definition)
        code, _ = code_generator.generate_code([flowchart])
        print(code)
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'typedef struct Test_s {',
            '  int x;',
            '  long *y;',
            '  long z[10];',
            '} Test_t;',
            '',
            'int main() {',
            '  return 0;',
            '}'])
        print(expected)
        assert code == expected, 'Structure definitions should be included in the source file.'
