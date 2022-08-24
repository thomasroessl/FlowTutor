from flowtutor.flowchart.assignment import Assignment


def test_new_assignment_has_tag():
    assignment = Assignment()
    assert assignment.tag
