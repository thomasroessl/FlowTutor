from multiprocessing import Queue


class StdinQueue:
    def __init__(self) -> None:
        self.input: Queue[str] = Queue()

    def readline(self) -> str:
        output = self.input.get()
        return output or ''

    def write(self, message: str) -> None:
        self.input.put(message)
