from typing import Any
from unittest.mock import patch
import pytest


from flowtutor.flowchart.flowchart import Flowchart
from flowtutor.flowchart.functionstart import FunctionStart
from flowtutor.flowchart.functionend import FunctionEnd
from flowtutor.flowchart.connector import Connector
from flowtutor.containers import Container
from flowtutor.flowchart.template import Template

from flowtutor.flowchart.node import dpg as node_dpg
from flowtutor.language_service import LanguageService


@patch.object(node_dpg, 'get_text_size', lambda _: (0, 0))
class TestFlowchart:

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

    def check_roots(self, flowchart):
        for i, node in enumerate(flowchart):
            if i == 0:
                assert isinstance(node, FunctionStart), 'The first node must be the function start'
            elif i == 1:
                assert isinstance(node, FunctionEnd), 'The last node must be the function end'

    def test_flowchart_initialize_root(self):
        flowchart = Flowchart('main', {})
        assert len(flowchart) == 2, 'A new flowchart should contain exactly 2 Nodes ("main" and "End")'
        self.check_roots(flowchart)

    def test_flowchart_add_nodes(self, nodes: dict[str, Any]):
        flowchart = Flowchart('main', {})
        node1 = Template(nodes['Declaration'])
        node2 = Template(nodes['Declaration'])
        flowchart.add_node(flowchart.root, node1)
        flowchart.add_node(node1, node2)
        assert len(flowchart) == 4, 'After adding 2 nodes, there should be 4 nodes in the flowchart'
        root_connection_0 = flowchart.root.find_connection(0)
        assert root_connection_0
        assert root_connection_0.dst_node == node1, 'There should be a connection from root to node1'
        node1_connection_0 = node1.find_connection(0)
        assert node1_connection_0
        assert node1_connection_0.dst_node == node2, 'There should be a connection from node1 to node2'

    def test_flowchart_add_loop(self, nodes: dict[str, Any]):
        flowchart = Flowchart('main', {})
        loop1 = Template(nodes['While loop'])
        flowchart.add_node(flowchart.root, loop1)
        assert len(flowchart) == 3, 'After adding a loop, there should be 3 nodes in the flowchart'
        root_connection_0 = flowchart.root.find_connection(0)
        assert root_connection_0
        assert root_connection_0.dst_node == loop1, 'There should be a connection from root to the loop'
        loop1_connection_1 = loop1.find_connection(1)
        assert loop1_connection_1
        assert loop1_connection_1.dst_node == loop1, 'There should be a connection from the loop to itself'

    def test_flowchart_add_conditional(self, nodes: dict[str, Any]):
        flowchart = Flowchart('main', {})
        node1 = Template(nodes['Conditional'])
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

    def test_flowchart_add_and_remove_node(self, nodes: dict[str, Any]):
        flowchart = Flowchart('main', {})
        node1 = Template(nodes['Declaration'])
        flowchart.add_node(flowchart.root, node1)
        assert len(flowchart) == 3, 'After adding a node, there should be 3 nodes in the flowchart'
        flowchart.remove_node(node1)
        assert len(flowchart) == 2, 'After removing the node, there should be 2 node in the flowchart'
        self.check_roots(flowchart)  # The remaining nodes should be the roots

    def test_flowchart_add_and_remove_conditional(self, nodes: dict[str, Any]):
        flowchart = Flowchart('main', {})
        conditional1 = Template(nodes['Conditional'])
        flowchart.add_node(flowchart.root, conditional1)
        assert len(flowchart) == 4, 'After adding a conditional, there should be 4 nodes in the flowchart'
        flowchart.remove_node(conditional1)
        assert len(flowchart) == 2, 'After removing the conditional, there should be 2 nodes in the flowchart'
        self.check_roots(flowchart)  # The remaining nodes should be the roots

    def test_flowchart_node_in_loop_body(self, nodes: dict[str, Any]):
        flowchart = Flowchart('main', {})
        loop1 = Template(nodes['While loop'])
        node1 = Template(nodes['Declaration'])
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

    def test_flowchart_add_and_remove_nested_conditional(self, nodes: dict[str, Any]):
        flowchart = Flowchart('main', {})

        conditional1 = Template(nodes['Conditional'])
        flowchart.add_node(flowchart.root, conditional1)
        assert len(flowchart) == 4, 'After adding a conditional, there should be 4 nodes in the flowchart'

        conditional2 = Template(nodes['Conditional'])
        flowchart.add_node(conditional1, conditional2, 1)
        assert len(flowchart) == 6, 'After adding a second conditional, there should be 6 nodes in the flowchart'
        conditional1_connection_1 = conditional1.find_connection(1)
        assert conditional1_connection_1
        assert conditional1_connection_1.dst_node == conditional2, ('There should be a connection '
                                                                    'from the first to the second conditional')

        assert conditional1.tag == conditional2.scope[-1], ('The scope of the second conditional '
                                                            'should be the first conditional')

        node1 = Template(nodes['Declaration'])
        flowchart.add_node(conditional2, node1, 0)
        assert len(flowchart) == 7, ('After adding a node to the second conditional, '
                                     'there should be 7 nodes in the flowchart')
        assert conditional2.tag == node1.scope[-1], 'The inner scope of node1 should be the second conditional'
        assert conditional1.tag == node1.scope[-2], 'The outer scope of node1 should be the first conditional'

        node2 = Template(nodes['Declaration'])
        flowchart.add_node(conditional2, node2, 0)
        assert len(flowchart) == 8, ('After adding another node to the second conditional, '
                                     'there should be 8 nodes in the flowchart')
        assert conditional2.tag == node2.scope[-1], 'The inner scope of node2 should be the second conditional'
        assert conditional1.tag == node2.scope[-2], 'The outer scope of node2 should be the first conditional'

        flowchart.remove_node(conditional1)
        assert len(flowchart) == 2, 'After removing the outer conditional, there should be 2 nodes in the flowchart'
        self.check_roots(flowchart)  # The remaining nodes should be the roots

    def test_flowchart_add_and_remove_nested_loops(self, nodes: dict[str, Any]):
        flowchart = Flowchart('main', {})

        loop1 = Template(nodes['While loop'])
        flowchart.add_node(flowchart.root, loop1)
        assert len(flowchart) == 3, 'After adding a loop, there should be 3 nodes in the flowchart'

        loop2 = Template(nodes['While loop'])
        flowchart.add_node(loop1, loop2, 1)
        assert len(flowchart) == 4, 'After adding another loop, there should be 4 nodes in the flowchart'
        assert loop1.tag == loop2.scope[-1], ('The scope of the second loop should be the first loop')

        node1 = Template(nodes['Declaration'])
        flowchart.add_node(loop2, node1, 1)
        assert len(flowchart) == 5, ('After adding a node to the second loop body,'
                                     'there should be 5 nodes in the flowchart')
        assert loop2.tag == node1.scope[-1], 'The inner scope of node1 should be the second conditional'
        assert loop1.tag == node1.scope[-2], 'The outer scope of node1 should be the first conditional'

        node2 = Template(nodes['Declaration'])
        flowchart.add_node(loop2, node2, 1)
        assert len(flowchart) == 6, ('After adding another node to the second loop body, '
                                     'there should be 6 nodes in the flowchart')
        assert loop2.tag == node2.scope[-1], 'The inner scope of node2 should be the second conditional'
        assert loop1.tag == node2.scope[-2], 'The outer scope of node2 should be the first conditional'

        flowchart.remove_node(loop1)
        assert len(flowchart) == 2, 'After removing the outer loop, there should be 1 node in the flowchart'
        self.check_roots(flowchart)  # The remaining nodes should be the roots
