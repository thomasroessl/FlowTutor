from multiprocessing import Queue


class StdinQueue:
    '''This class is used to override the system stdin, to enable communication with debugged programs through code.'''

    def __init__(self) -> None:
        self.input: Queue[str] = Queue()
        '''An instance of a Queue, used for communication.'''

    def readline(self) -> str:
        '''Read a line from the Queue.'''
        output = self.input.get()
        return output or ''

    def write(self, message: str) -> None:
        '''Write to the Queue.'''
        self.input.put(message)
