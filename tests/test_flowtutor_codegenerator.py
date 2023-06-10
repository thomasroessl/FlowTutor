from unittest.mock import patch
import pytest

from flowtutor.codegenerator import CodeGenerator
from flowtutor.containers import Container
from flowtutor.flowchart.assignment import Assignment
from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.declaration import Declaration
from flowtutor.flowchart.declarations import Declarations
from flowtutor.flowchart.dowhileloop import DoWhileLoop
from flowtutor.flowchart.flowchart import Flowchart
from flowtutor.flowchart.forloop import ForLoop
from flowtutor.flowchart.struct_definition import StructDefinition
from flowtutor.flowchart.struct_member import StructMember
from flowtutor.flowchart.type_definition import TypeDefinition
from flowtutor.flowchart.whileloop import WhileLoop
from flowtutor.flowchart.input import Input
from flowtutor.flowchart.output import Output
from flowtutor.flowchart.parameter import Parameter
from flowtutor.flowchart.snippet import Snippet
from flowtutor.flowchart.template import Template

from flowtutor.language import Language
from flowtutor.flowchart.node import dpg as node_dpg


@patch.object(node_dpg, 'get_text_size', lambda _: (0, 0))
class TestCodeGenerator:

    @pytest.fixture(scope='session')
    def code_generator(self) -> CodeGenerator:
        container = Container()
        container.init_resources()
        container.wire(modules=['flowtutor.codegenerator'])
        return CodeGenerator()

    def test_code_from_empty_flowchart(self, code_generator: CodeGenerator):
        flowchart = Flowchart('main')
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

    def test_code_from_includes(self, code_generator: CodeGenerator):
        flowchart = Flowchart('main')
        flowchart.includes.append('test1')
        flowchart.includes.append('test2')
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

    @pytest.mark.parametrize('data_type', Language.get_data_types())
    def test_code_from_declaration(self, data_type, code_generator: CodeGenerator):
        flowchart = Flowchart('main')
        declaration = Declaration()
        declaration.var_name = 'x'
        declaration.var_type = data_type
        declaration.var_value = '3'
        flowchart.add_node(flowchart.root, declaration)
        code, _ = code_generator.generate_code([flowchart])
        print(code)
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            f'  {data_type} x = 3;',
            '  return 0;',
            '}'])
        print(expected)
        assert code == expected, 'Declaration with value.'

    @pytest.mark.parametrize('data_type', Language.get_data_types())
    def test_code_from_static_declaration(self, data_type, code_generator: CodeGenerator):
        flowchart = Flowchart('main')
        declaration = Declaration()
        declaration.var_name = 'x'
        declaration.is_static = True
        declaration.var_type = data_type
        declaration.var_value = '3'
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

    @pytest.mark.parametrize('data_type', Language.get_data_types())
    def test_code_from_pointer_declaration(self, data_type, code_generator: CodeGenerator):
        flowchart = Flowchart('main')
        declaration = Declaration()
        declaration.var_name = 'x'
        declaration.var_type = data_type
        declaration.is_pointer = True
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

    @pytest.mark.parametrize('data_type', Language.get_data_types())
    def test_code_from_declarations(self, data_type, code_generator: CodeGenerator):
        flowchart = Flowchart('main')
        declarations = Declarations()
        declarations.declarations = [
            {
                'var_name': 'x',
                'var_type': data_type,
                'var_value': '1',
                'array_size': '',
                'is_array': False,
                'is_pointer':  False,
                'is_static':  False
            },
            {
                'var_name': 'y',
                'var_type': data_type,
                'var_value': '2',
                'array_size': '',
                'is_array': False,
                'is_pointer':  False,
                'is_static':  True
            },
            {
                'var_name': 'z',
                'var_type': data_type,
                'var_value': '',
                'array_size': '',
                'is_array': False,
                'is_pointer':  True,
                'is_static':  False
            }
        ]
        flowchart.add_node(flowchart.root, declarations)
        code, _ = code_generator.generate_code([flowchart])
        print(code)
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            f'  {data_type} x = 1;',
            f'  static {data_type} y = 2;',
            f'  {data_type} *z;',
            '  return 0;',
            '}'])
        print(expected)
        assert code == expected, 'Multiple Declarations with values.'

    def test_code_from_assignment(self, code_generator: CodeGenerator):
        flowchart = Flowchart('main')
        assignment = Assignment()
        assignment.var_name = 'x'
        assignment.var_value = '3'
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

    def test_code_from_assignment_with_comment(self, code_generator: CodeGenerator):
        flowchart = Flowchart('main')
        assignment = Assignment()
        assignment.var_name = 'x'
        assignment.var_value = '3'
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

    def test_code_from_array_assignment(self, code_generator: CodeGenerator):
        flowchart = Flowchart('main')
        assignment = Assignment()
        assignment.var_name = 'x'
        assignment.var_offset = '0'
        assignment.var_value = '3'
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

    def test_code_from_conditional(self, code_generator: CodeGenerator):
        flowchart = Flowchart('main')
        conditional = Conditional()
        conditional.condition = 'x > 5'
        flowchart.add_node(flowchart.root, conditional)
        code, _ = code_generator.generate_code([flowchart])
        print(repr(code))
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            '  if(x > 5) {',
            '  }',
            '  return 0;',
            '}'])
        print(repr(expected))
        assert code == expected, 'Conditional.'

    def test_code_from_conditional_with_one_branch(self, code_generator: CodeGenerator):
        flowchart = Flowchart('main')
        conditional = Conditional()
        conditional.condition = 'x > 5'
        flowchart.add_node(flowchart.root, conditional)

        assignment = Assignment()
        assignment.var_name = 'x'
        assignment.var_value = '3'
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
        print(repr(code))
        print(repr(expected))
        assert code == expected, 'Conditional.'

    def test_code_from_conditional_with_two_branches(self, code_generator: CodeGenerator):
        flowchart = Flowchart('main')
        conditional = Conditional()
        conditional.condition = 'x > 5'
        flowchart.add_node(flowchart.root, conditional)

        assignment1 = Assignment()
        assignment1.var_name = 'x'
        assignment1.var_value = '3'
        flowchart.add_node(conditional, assignment1, 1)

        assignment2 = Assignment()
        assignment2.var_name = 'x'
        assignment2.var_value = '5'
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
        print(repr(code))
        print(repr(expected))
        assert code == expected, 'Conditional.'

    def test_code_from_whileloop(self, code_generator: CodeGenerator):
        flowchart = Flowchart('main')
        loop = WhileLoop()
        loop.condition = 'x > 5'
        flowchart.add_node(flowchart.root, loop)

        assignment = Assignment()
        assignment.var_name = 'x'
        assignment.var_value = '3'
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
        print(repr(code))
        print(repr(expected))
        assert code == expected, 'While-Loop.'

    def test_code_from_do_while_loop(self, code_generator: CodeGenerator):
        flowchart = Flowchart('main')
        loop = DoWhileLoop()
        loop.condition = 'x > 5'
        flowchart.add_node(flowchart.root, loop)

        assignment = Assignment()
        assignment.var_name = 'x'
        assignment.var_value = '3'
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
        print(repr(code))
        print(repr(expected))
        assert code == expected, 'While-Loop.'
        pass

    def test_code_from_forloop(self, code_generator: CodeGenerator):
        flowchart = Flowchart('main')
        loop = ForLoop()
        loop.var_name = 'i'
        loop.start_value = '0'
        loop.condition = 'i < 10'
        loop.update = 'i++'
        flowchart.add_node(flowchart.root, loop)

        assignment = Assignment()
        assignment.var_name = 'x'
        assignment.var_value = 'x + 3'
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
        print(repr(code))
        print(repr(expected))
        assert code == expected, 'For-Loop.'

    @pytest.mark.parametrize('data_type_format', list(zip(Language.get_data_types(), Language.get_format_specifiers())))
    def test_code_from_input(self, data_type_format, code_generator: CodeGenerator):
        data_type, format_specifier = data_type_format
        flowchart = Flowchart('main')

        declaration = Declaration()
        declaration.var_name = 'x'
        declaration.var_type = data_type

        input = Input()
        input.var_name = 'x'

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
        print(repr(code))
        print(repr(expected))
        assert code == expected, 'Input.'

    def test_code_from_input_undeclared(self, code_generator: CodeGenerator):
        flowchart = Flowchart('main')

        input = Input()
        input.var_name = 'x'

        flowchart.add_node(flowchart.root, input)

        code, _ = code_generator.generate_code([flowchart])
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            '  // x is not declared!',
            '  return 0;',
            '}'])
        print(code)
        print(expected)
        print(repr(code))
        print(repr(expected))
        assert code == expected, 'Input undeclared.'

    def test_code_from_output(self, code_generator: CodeGenerator):
        flowchart = Flowchart('main')

        output = Output()
        output.format_string = 'This is the output.'

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
        print(repr(code))
        print(repr(expected))
        assert code == expected, 'Output.'

    def test_code_from_snippet(self, code_generator: CodeGenerator):
        flowchart = Flowchart('main')

        snippet = Snippet()
        snippet.code = 'printf("Test Code line 1");\nprintf("Test Code line 2");'

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
        print(repr(code))
        print(repr(expected))
        assert code == expected, 'Snippet.'

    def test_code_from_output_with_arguments(self, code_generator: CodeGenerator):
        flowchart = Flowchart('main')

        output = Output()
        output.format_string = 'This is the output: %d'
        output.arguments = '5'

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
        print(repr(code))
        print(repr(expected))
        assert code == expected, 'Output with arguments.'

    def test_code_from_multiple_empty_functions(self, code_generator: CodeGenerator):
        flowchart1 = Flowchart('main')

        flowchart2 = Flowchart('func1')

        flowchart3 = Flowchart('func2')

        code, _ = code_generator.generate_code([flowchart1, flowchart2, flowchart3])
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
        print(repr(code))
        print(repr(expected))
        assert code == expected, 'Declaration of multiple empty functions.'

    def test_code_from_multiple_empty_functions_with_arguments(self, code_generator: CodeGenerator):
        flowchart1 = Flowchart('main')

        flowchart2 = Flowchart('func1')

        flowchart3 = Flowchart('func2')
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

        code, _ = code_generator.generate_code([flowchart1, flowchart2, flowchart3])
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
        print(repr(code))
        print(repr(expected))
        assert code == expected, 'Declaration of multiple empty functions.'

    def test_code_from_typedef(self, code_generator: CodeGenerator):
        flowchart = Flowchart('main')
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

    def test_code_from_struct(self, code_generator: CodeGenerator):
        flowchart = Flowchart('main')
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

    def test_code_from_template(self, code_generator: CodeGenerator):
        flowchart = Flowchart('main')

        template = Template(
            {
                'label': 'Open File',
                'shape_id': 'data',
                'color': '(147, 171, 255)',
                'parameters': [
                    {
                        'name': 'VAR_NAME',
                        'label': 'Name'
                    },
                    {
                        'name': 'FILE',
                        'label': 'File Path'
                    },
                    {
                        'name': 'MODE',
                        'label': 'Mode',
                        'default': 'r',
                        'options': [
                            'r',
                            'r+',
                            'w',
                            'w+',
                            'a',
                            'a+'
                        ]
                    }
                ],
                'body': [
                    'FILE *${VAR_NAME};',
                    '${VAR_NAME} = fopen(${FILE}, \"${MODE}\");'
                ]
            }
        )

        template.values['VAR_NAME'] = 'x'
        template.values['FILE'] = '"/test/path/to/file"'
        template.values['MODE'] = 'w+'

        flowchart.add_node(flowchart.root, template)

        code, _ = code_generator.generate_code([flowchart])
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            '  FILE *x;',
            '  x = fopen("/test/path/to/file", "w+");',
            '  return 0;',
            '}'])
        print(code)
        print(expected)
        print(repr(code))
        print(repr(expected))
        assert code == expected, 'Template.'
