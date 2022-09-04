from unittest.mock import patch
from flowtutor.flowchart.assignment import Assignment
from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.flowchart import Flowchart
from flowtutor.flowchart.loop import Loop


def test_new_assignment_has_tag():
    assignment = Assignment()
    assert assignment.tag


@patch('flowtutor.flowchart.connection.dpg')
def test_flowchart_add_assignments(dpg_mock):
    flowchart = Flowchart()
    assignment1 = Assignment()
    assignment2 = Assignment()
    flowchart.add_node(flowchart.root, assignment1)
    flowchart.add_node(assignment1, assignment2)
    assert len(flowchart) == 3


@patch('flowtutor.flowchart.connection.dpg')
def test_flowchart_add_loops(dpg_mock):
    flowchart = Flowchart()
    loop1 = Loop()
    loop2 = Loop()
    flowchart.add_node(flowchart.root, loop1)
    flowchart.add_node(loop1, loop2)
    assert len(flowchart) == 3


@patch('flowtutor.flowchart.connection.dpg')
def test_flowchart_conditional_in_loop_body(dpg_mock):
    flowchart = Flowchart()
    loop1 = Loop()
    conditional1 = Conditional()
    flowchart.add_node(flowchart.root, loop1)
    flowchart.add_node(loop1, conditional1, 1)
    assert len(flowchart) == 4
