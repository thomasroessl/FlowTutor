from typing import Optional, Any

from flowtutor.flowchart.assignment import Assignment
from flowtutor.flowchart.call import Call
from flowtutor.flowchart.declaration import Declaration
from flowtutor.flowchart.conditional import Conditional
from flowtutor.flowchart.forloop import ForLoop
from flowtutor.flowchart.whileloop import WhileLoop
from flowtutor.flowchart.dowhileloop import DoWhileLoop
from flowtutor.flowchart.input import Input
from flowtutor.flowchart.output import Output
from flowtutor.flowchart.snippet import Snippet


class NodesService:

    def get_node_types(self) -> list[tuple[str, type, Optional[Any]]]:
        return [
            ('Assignment', Assignment, None),
            ('Call', Call, None),
            ('Declaration', Declaration, None),
            ('Conditional', Conditional, None),
            ('For Loop', ForLoop, None),
            ('While Loop', WhileLoop, None),
            ('Do-While Loop', DoWhileLoop, None),
            ('Input', Input, None),
            ('Output', Output, None),
            ('Code Snippet', Snippet, None)
        ]
