class SlotRotator:
    def __init__(self, values: list, offset: int = 0):
        self._values = values
        self._offset = offset
        self._counter = 0

    def next(self) -> str:
        idx = (self._counter + self._offset) % len(self._values)
        self._counter += 1
        return self._values[idx]
