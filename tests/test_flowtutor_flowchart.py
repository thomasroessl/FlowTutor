import pytest

from flowtutor.flowchart.assignment import Assignment
from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.flowchart import Flowchart
from flowtutor.flowchart.input import Input
from flowtutor.flowchart.loop import Loop
from flowtutor.flowchart.output import Output


@pytest.mark.parametrize('node_class', [
    Assignment,
    Conditional,
    Input,
    Loop,
    Output
])
def test_new_node_has_tag(node_class):
    node = node_class()
    assert node.tag


def test_flowchart_initialize_root():
    flowchart = Flowchart()
    assert len(flowchart) == 1


def test_flowchart_add_assignments():
    flowchart = Flowchart()
    assignment1 = Assignment()
    assignment2 = Assignment()
    flowchart.add_node(flowchart.root, assignment1)
    flowchart.add_node(assignment1, assignment2)
    assert len(flowchart) == 3


def test_flowchart_add_loops():
    flowchart = Flowchart()
    loop1 = Loop()
    loop2 = Loop()
    flowchart.add_node(flowchart.root, loop1)
    flowchart.add_node(loop1, loop2)
    assert len(flowchart) == 3


def test_flowchart_conditional_in_loop_body():
    flowchart = Flowchart()
    loop1 = Loop()
    conditional1 = Conditional()
    flowchart.add_node(flowchart.root, loop1)
    flowchart.add_node(loop1, conditional1, 1)
    assert len(flowchart) == 4


def test_flowchart_add_and_remove_assignment():
    flowchart = Flowchart()
    assignment1 = Assignment()
    flowchart.add_node(flowchart.root, assignment1)
    assert len(flowchart) == 2
    flowchart.remove_node(assignment1)
    assert len(flowchart) == 1


def test_flowchart_add_and_remove_conditional():
    flowchart = Flowchart()
    conditional1 = Conditional()
    flowchart.add_node(flowchart.root, conditional1)
    assert len(flowchart) == 3
    flowchart.remove_node(conditional1)
    assert len(flowchart) == 1


def test_flowchart_add_and_remove_nested_conditional():
    flowchart = Flowchart()

    conditional1 = Conditional()
    flowchart.add_node(flowchart.root, conditional1)
    assert len(flowchart) == 3

    conditional2 = Conditional()
    flowchart.add_node(conditional1, conditional2, 1)
    assert len(flowchart) == 5

    assignment1 = Assignment()
    flowchart.add_node(conditional1, assignment1, 0)
    assert len(flowchart) == 6

    assignment2 = Assignment()
    flowchart.add_node(conditional2, assignment2, 0)
    assert len(flowchart) == 7

    flowchart.remove_node(conditional2)
    assert len(flowchart) == 4


def test_flowchart_add_and_remove_nested_loops():
    flowchart = Flowchart()

    loop1 = Loop()
    flowchart.add_node(flowchart.root, loop1)
    assert len(flowchart) == 2

    loop2 = Loop()
    flowchart.add_node(loop1, loop2, 1)
    assert len(flowchart) == 3

    assignment1 = Assignment()
    flowchart.add_node(loop1, assignment1, 0)
    assert len(flowchart) == 4

    assignment2 = Assignment()
    flowchart.add_node(loop2, assignment2, 0)
    assert len(flowchart) == 5

    flowchart.remove_node(loop2)
    assert len(flowchart) == 4
