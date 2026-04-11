import abc
from typing import Any


class BaseSampler(abc.ABC):

    @abc.abstractmethod
    def sample(self) -> dict[str, Any]:
        """Return a dict of variables for prompt rendering."""
        pass
