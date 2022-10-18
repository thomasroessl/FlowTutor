from unittest.mock import patch
import pytest

from flowtutor.codegenerator import CodeGenerator
from flowtutor.flowchart.assignment import Assignment
from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.declaration import Declaration
from flowtutor.flowchart.flowchart import Flowchart
from flowtutor.flowchart.input import Input
from flowtutor.flowchart.loop import Loop
from flowtutor.flowchart.output import Output
from flowtutor.language import Language

from flowtutor.flowchart.node import dpg as node_dpg


@patch.object(node_dpg, 'get_text_size', lambda _: (0, 0))
class TestCodeGenerator:

    def test_code_from_empty_flowchart(self):
        flowchart = Flowchart()
        code_generator = CodeGenerator()
        code = '\n'.join(code_generator.generate_code(flowchart, flowchart.root))
        print(code)
        expected = '\n'.join([
            'int main() {',
            '  return 0;',
            '}'])
        print(expected)
        assert code == expected, 'An empty flowchart should produce a main function, which returns 0.'

    @pytest.mark.parametrize('data_type', Language.get_data_types())
    def test_code_from_declaration(self, data_type):
        flowchart = Flowchart()
        declaration = Declaration()
        declaration.var_name = 'x'
        declaration.var_type = data_type
        declaration.var_value = '3'
        flowchart.add_node(flowchart.root, declaration)
        code_generator = CodeGenerator()
        code = '\n'.join(code_generator.generate_code(flowchart, flowchart.root))
        print(code)
        expected = '\n'.join([
            'int main() {',
            f'  {data_type} x = 3;',
            '  return 0;',
            '}'])
        print(expected)
        assert code == expected, 'Declaration with value.'

    @pytest.mark.parametrize('data_type', Language.get_data_types())
    def test_code_from_pointer_declaration(self, data_type):
        flowchart = Flowchart()
        declaration = Declaration()
        declaration.var_name = 'x'
        declaration.var_type = data_type
        declaration.is_pointer = True
        flowchart.add_node(flowchart.root, declaration)
        code_generator = CodeGenerator()
        code = '\n'.join(code_generator.generate_code(flowchart, flowchart.root))
        print(code)
        expected = '\n'.join([
            'int main() {',
            f'  {data_type} *x;',
            '  return 0;',
            '}'])
        print(expected)
        assert code == expected, 'Pointer declaration.'

    def test_code_from_assignment(self):
        flowchart = Flowchart()
        assignment = Assignment()
        assignment.var_name = 'x'
        assignment.var_value = '3'
        flowchart.add_node(flowchart.root, assignment)
        code_generator = CodeGenerator()
        code = '\n'.join(code_generator.generate_code(flowchart, flowchart.root))
        print(code)
        expected = '\n'.join([
            'int main() {',
            '  x = 3;',
            '  return 0;',
            '}'])
        print(expected)
        assert code == expected, 'Assignment.'

    def test_code_from_assignment_with_comment(self):
        flowchart = Flowchart()
        assignment = Assignment()
        assignment.var_name = 'x'
        assignment.var_value = '3'
        assignment.comment = 'This is a comment'
        flowchart.add_node(flowchart.root, assignment)
        code_generator = CodeGenerator()
        code = '\n'.join(code_generator.generate_code(flowchart, flowchart.root))
        print(code)
        expected = '\n'.join([
            'int main() {',
            '  // This is a comment',
            '  x = 3;',
            '  return 0;',
            '}'])
        print(expected)
        assert code == expected, 'Assignment.'

    def test_code_from_array_assignment(self):
        flowchart = Flowchart()
        assignment = Assignment()
        assignment.var_name = 'x'
        assignment.var_offset = '0'
        assignment.var_value = '3'
        flowchart.add_node(flowchart.root, assignment)
        code_generator = CodeGenerator()
        code = '\n'.join(code_generator.generate_code(flowchart, flowchart.root))
        print(code)
        expected = '\n'.join([
            'int main() {',
            '  x[0] = 3;',
            '  return 0;',
            '}'])
        print(expected)
        assert code == expected, 'Assignment.'

    def test_code_from_conditional(self):
        flowchart = Flowchart()
        conditional = Conditional()
        conditional.condition = 'x > 5'
        flowchart.add_node(flowchart.root, conditional)
        code_generator = CodeGenerator()
        code = '\n'.join(code_generator.generate_code(flowchart, flowchart.root))
        print(repr(code))
        expected = '\n'.join([
            'int main() {',
            '  if(x > 5) {',
            '  }',
            '  return 0;',
            '}'])
        print(repr(expected))
        assert code == expected, 'Conditional.'

    def test_code_from_conditional_with_one_branch(self):
        flowchart = Flowchart()
        conditional = Conditional()
        conditional.condition = 'x > 5'
        flowchart.add_node(flowchart.root, conditional)

        assignment = Assignment()
        assignment.var_name = 'x'
        assignment.var_value = '3'
        flowchart.add_node(conditional, assignment, 1)

        code_generator = CodeGenerator()
        code = '\n'.join(code_generator.generate_code(flowchart, flowchart.root))
        expected = '\n'.join([
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

    def test_code_from_conditional_with_two_branches(self):
        flowchart = Flowchart()
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

        code_generator = CodeGenerator()
        code = '\n'.join(code_generator.generate_code(flowchart, flowchart.root))
        expected = '\n'.join([
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

    def test_code_from_while_loop(self):
        flowchart = Flowchart()
        loop = Loop()
        loop.condition = 'x > 5'
        flowchart.add_node(flowchart.root, loop)

        assignment = Assignment()
        assignment.var_name = 'x'
        assignment.var_value = '3'
        flowchart.add_node(loop, assignment, 1)

        code_generator = CodeGenerator()
        code = '\n'.join(code_generator.generate_code(flowchart, flowchart.root))
        expected = '\n'.join([
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

    def test_code_from_for_loop(self):
        flowchart = Flowchart()
        loop = Loop()
        loop.loop_type = 'for'
        loop.var_name = 'i'
        loop.start_value = '0'
        loop.condition = 'i < 10'
        loop.update = 'i++'
        flowchart.add_node(flowchart.root, loop)

        assignment = Assignment()
        assignment.var_name = 'x'
        assignment.var_value = 'x + 3'
        flowchart.add_node(loop, assignment, 1)

        code_generator = CodeGenerator()
        code = '\n'.join(code_generator.generate_code(flowchart, flowchart.root))
        expected = '\n'.join([
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
    def test_code_from_input(self, data_type_format):
        data_type, format_specifier = data_type_format
        flowchart = Flowchart()

        declaration = Declaration()
        declaration.var_name = 'x'
        declaration.var_type = data_type

        input = Input()
        input.var_name = 'x'

        flowchart.add_node(flowchart.root, declaration)
        flowchart.add_node(declaration, input)

        code_generator = CodeGenerator()
        code = '\n'.join(code_generator.generate_code(flowchart, flowchart.root))
        expected = '\n'.join([
            '#include <stdio.h>',
            '',
            'int main() {',
            f'  {data_type} x;',
            f'  scanf("{format_specifier}", x);',
            '  return 0;',
            '}'])
        print(code)
        print(expected)
        print(repr(code))
        print(repr(expected))
        assert code == expected, 'Input.'

    def test_code_from_input_undeclared(self):
        flowchart = Flowchart()

        input = Input()
        input.var_name = 'x'

        flowchart.add_node(flowchart.root, input)

        code_generator = CodeGenerator()
        code = '\n'.join(code_generator.generate_code(flowchart, flowchart.root))
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

    def test_code_from_output(self):
        flowchart = Flowchart()

        output = Output()
        output.format_string = 'This is the output.'

        flowchart.add_node(flowchart.root, output)

        code_generator = CodeGenerator()
        code = '\n'.join(code_generator.generate_code(flowchart, flowchart.root))
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

    def test_code_from_output_with_arguments(self):
        flowchart = Flowchart()

        output = Output()
        output.format_string = 'This is the output: %d'
        output.arguments = '5'

        flowchart.add_node(flowchart.root, output)

        code_generator = CodeGenerator()
        code = '\n'.join(code_generator.generate_code(flowchart, flowchart.root))
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
