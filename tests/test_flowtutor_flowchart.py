from unittest.mock import patch
from flowtutor.flowchart.assignment import Assignment
from flowtutor.flowchart.flowchart import Flowchart


def test_new_assignment_has_tag():
    assignment = Assignment()
    assert assignment.tag


@patch('flowtutor.flowchart.connection.dpg')
def test_flowchart_add_assignment(dpg_mock):
    flowchart = Flowchart()
    assignment1 = Assignment()
    assignment2 = Assignment()
    flowchart.add_node(assignment1, None)
    flowchart.add_node(assignment2, assignment1)
    assert len(flowchart.nodes) == 2
    assert len(flowchart.connections) == 1
