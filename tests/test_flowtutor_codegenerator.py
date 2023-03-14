from unittest.mock import patch
import pytest

from flowtutor.codegenerator import CodeGenerator
from flowtutor.containers import Container
from flowtutor.flowchart.assignment import Assignment
from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.declaration import Declaration
from flowtutor.flowchart.dowhileloop import DoWhileLoop
from flowtutor.flowchart.flowchart import Flowchart
from flowtutor.flowchart.forloop import ForLoop
from flowtutor.flowchart.whileloop import WhileLoop
from flowtutor.flowchart.input import Input
from flowtutor.flowchart.output import Output
from flowtutor.flowchart.parameter import Parameter
from flowtutor.flowchart.snippet import Snippet

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
