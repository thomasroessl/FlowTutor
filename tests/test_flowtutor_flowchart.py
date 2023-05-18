from unittest.mock import patch
import pytest

from flowtutor.flowchart.assignment import Assignment
from flowtutor.flowchart.declaration import Declaration
from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.flowchart import Flowchart
from flowtutor.flowchart.forloop import ForLoop
from flowtutor.flowchart.input import Input
from flowtutor.flowchart.output import Output
from flowtutor.flowchart.snippet import Snippet
from flowtutor.flowchart.whileloop import WhileLoop
from flowtutor.flowchart.functionstart import FunctionStart
from flowtutor.flowchart.functionend import FunctionEnd
from flowtutor.flowchart.connector import Connector

from flowtutor.flowchart.node import dpg as node_dpg

SIMPLE_NODES = [  # Nodes with exactly one input and one output
    Declaration,
    Assignment,
    Input,
    Output,
    Snippet
]

ALL_NODES = [
    Declaration,
    Assignment,
    Conditional,
    Input,
    WhileLoop,
    ForLoop,
    Output,
    Snippet,
    FunctionStart
]


@patch.object(node_dpg, 'get_text_size', lambda _: (0, 0))
class TestFlowchart:

    @pytest.mark.parametrize('node_class', ALL_NODES)
    def test_new_node_has_tag(self, node_class):
        node = node_class()
        assert node.tag

    def check_roots(self, flowchart):
        for i, node in enumerate(flowchart):
            if i == 0:
                assert isinstance(node, FunctionStart), 'The first node must be the function start'
            elif i == 1:
                assert isinstance(node, FunctionEnd), 'The last node must be the function end'

    def test_flowchart_initialize_root(self):
        flowchart = Flowchart('main')
        assert len(flowchart) == 2, 'A new flowchart should contain exactly 2 Nodes ("main" and "End")'
        self.check_roots(flowchart)

    @pytest.mark.parametrize('node_class', SIMPLE_NODES)
    def test_flowchart_add_nodes(self, node_class):
        flowchart = Flowchart('main')
        node1 = node_class()
        node2 = node_class()
        flowchart.add_node(flowchart.root, node1)
        flowchart.add_node(node1, node2)
        assert len(flowchart) == 4, 'After adding 2 nodes, there should be 4 nodes in the flowchart'
        root_connection_0 = flowchart.root.find_connection(0)
        assert root_connection_0
        assert root_connection_0.dst_node == node1, 'There should be a connection from root to node1'
        node1_connection_0 = node1.find_connection(0)
        assert node1_connection_0
        assert node1_connection_0.dst_node == node2, 'There should be a connection from node1 to node2'

    def test_flowchart_add_loop(self):
        flowchart = Flowchart('main')
        loop1 = WhileLoop()
        flowchart.add_node(flowchart.root, loop1)
        assert len(flowchart) == 3, 'After adding a loop, there should be 3 nodes in the flowchart'
        root_connection_0 = flowchart.root.find_connection(0)
        assert root_connection_0
        assert root_connection_0.dst_node == loop1, 'There should be a connection from root to the loop'
        loop1_connection_1 = loop1.find_connection(1)
        assert loop1_connection_1
        assert loop1_connection_1.dst_node == loop1, 'There should be a connection from the loop to itself'

    def test_flowchart_add_conditional(self):
        flowchart = Flowchart('main')
        node1 = Conditional()
        flowchart.add_node(flowchart.root, node1)
        assert len(flowchart) == 4, ('After adding a conditional, there should be 4 nodes in the flowchart'
                                     ' (including the conditional connector)')
        root_connection_0 = flowchart.root.find_connection(0)
        assert root_connection_0
        assert root_connection_0.dst_node == node1, 'There should be a connection from root to the conditional'
        node1_connection_0 = node1.find_connection(0)
        assert node1_connection_0
        connector_0 = node1_connection_0.dst_node
        assert isinstance(connector_0, Connector), 'There should be a connection from the conditional to the connector'
        node1_connection_1 = node1.find_connection(1)
        assert node1_connection_1
        connector_1 = node1_connection_1.dst_node
        assert isinstance(connector_1, Connector), ('There should be a second connection '
                                                    'from the conditional to the connector')
        assert connector_0 == connector_1, 'The connections of the conditional should be to the same connector'

    @pytest.mark.parametrize('node_class', SIMPLE_NODES)
    def test_flowchart_add_and_remove_node(self, node_class):
        flowchart = Flowchart('main')
        node1 = node_class()
        flowchart.add_node(flowchart.root, node1)
        assert len(flowchart) == 3, 'After adding a node, there should be 3 nodes in the flowchart'
        flowchart.remove_node(node1)
        assert len(flowchart) == 2, 'After removing the node, there should be 2 node in the flowchart'
        self.check_roots(flowchart)  # The remaining nodes should be the roots

    def test_flowchart_add_and_remove_conditional(self):
        flowchart = Flowchart('main')
        conditional1 = Conditional()
        flowchart.add_node(flowchart.root, conditional1)
        assert len(flowchart) == 4, 'After adding a conditional, there should be 4 nodes in the flowchart'
        flowchart.remove_node(conditional1)
        assert len(flowchart) == 2, 'After removing the conditional, there should be 2 nodes in the flowchart'
        self.check_roots(flowchart)  # The remaining nodes should be the roots

    @pytest.mark.parametrize('node_class', SIMPLE_NODES)
    def test_flowchart_node_in_loop_body(self, node_class):
        flowchart = Flowchart('main')
        loop1 = WhileLoop()
        node1 = node_class()
        flowchart.add_node(flowchart.root, loop1)
        flowchart.add_node(loop1, node1, 1)
        assert len(flowchart) == 4, ('After adding a loop and a node in the loop body, '
                                     'there should be 4 nodes in the flowchart')
        loop_connection_1 = loop1.find_connection(1)
        assert loop_connection_1
        assert loop_connection_1.dst_node == node1, 'There should be a connection from the loop to the node'
        assert loop1.tag == node1.scope[-1], 'The scope of the node should be the loop'
        node1_connection_0 = node1.find_connection(0)
        assert node1_connection_0
        assert node1_connection_0.dst_node == loop1, 'There should be a connection from the node to the loop'

    @pytest.mark.parametrize('node_class', SIMPLE_NODES)
    def test_flowchart_add_and_remove_nested_conditional(self, node_class):
        flowchart = Flowchart('main')

        conditional1 = Conditional()
        flowchart.add_node(flowchart.root, conditional1)
        assert len(flowchart) == 4, 'After adding a conditional, there should be 4 nodes in the flowchart'

        conditional2 = Conditional()
        flowchart.add_node(conditional1, conditional2, 1)
        assert len(flowchart) == 6, 'After adding a second conditional, there should be 6 nodes in the flowchart'
        conditional1_connection_1 = conditional1.find_connection(1)
        assert conditional1_connection_1
        assert conditional1_connection_1.dst_node == conditional2, ('There should be a connection '
                                                                    'from the first to the second conditional')

        assert conditional1.tag == conditional2.scope[-1], ('The scope of the second conditional '
                                                            'should be the first conditional')

        node1 = node_class()
        flowchart.add_node(conditional2, node1, 0)
        assert len(flowchart) == 7, ('After adding a node to the second conditional, '
                                     'there should be 7 nodes in the flowchart')
        assert conditional2.tag == node1.scope[-1], 'The inner scope of node1 should be the second conditional'
        assert conditional1.tag == node1.scope[-2], 'The outer scope of node1 should be the first conditional'

        node2 = node_class()
        flowchart.add_node(conditional2, node2, 0)
        assert len(flowchart) == 8, ('After adding another node to the second conditional, '
                                     'there should be 8 nodes in the flowchart')
        assert conditional2.tag == node2.scope[-1], 'The inner scope of node2 should be the second conditional'
        assert conditional1.tag == node2.scope[-2], 'The outer scope of node2 should be the first conditional'

        flowchart.remove_node(conditional1)
        assert len(flowchart) == 2, 'After removing the outer conditional, there should be 2 nodes in the flowchart'
        self.check_roots(flowchart)  # The remaining nodes should be the roots

    @pytest.mark.parametrize('node_class', SIMPLE_NODES)
    def test_flowchart_add_and_remove_nested_loops(self, node_class):
        flowchart = Flowchart('main')

        loop1 = WhileLoop()
        flowchart.add_node(flowchart.root, loop1)
        assert len(flowchart) == 3, 'After adding a loop, there should be 3 nodes in the flowchart'

        loop2 = WhileLoop()
        flowchart.add_node(loop1, loop2, 1)
        assert len(flowchart) == 4, 'After adding another loop, there should be 4 nodes in the flowchart'
        assert loop1.tag == loop2.scope[-1], ('The scope of the second loop should be the first loop')

        node1 = node_class()
        flowchart.add_node(loop2, node1, 1)
        assert len(flowchart) == 5, ('After adding a node to the second loop body,'
                                     'there should be 5 nodes in the flowchart')
        assert loop2.tag == node1.scope[-1], 'The inner scope of node1 should be the second conditional'
        assert loop1.tag == node1.scope[-2], 'The outer scope of node1 should be the first conditional'

        node2 = node_class()
        flowchart.add_node(loop2, node2, 1)
        assert len(flowchart) == 6, ('After adding another node to the second loop body, '
                                     'there should be 6 nodes in the flowchart')
        assert loop2.tag == node2.scope[-1], 'The inner scope of node2 should be the second conditional'
        assert loop1.tag == node2.scope[-2], 'The outer scope of node2 should be the first conditional'

        flowchart.remove_node(loop1)
        assert len(flowchart) == 2, 'After removing the outer loop, there should be 1 node in the flowchart'
        self.check_roots(flowchart)  # The remaining nodes should be the roots
