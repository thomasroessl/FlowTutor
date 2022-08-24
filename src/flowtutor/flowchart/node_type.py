from enum import Enum

class NodeType(Enum):
    Assignment = 1
    Conditional = 2
    Loop = 3
    Input = 4
    Output = 5
    Connector = 5
