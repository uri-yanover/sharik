from abc import ABC, abstractmethod
from pydantic.dataclasses import dataclass
from typing import Iterable, Tuple, Callable

ContentSupplier = Callable[[], bytes]


@dataclass
class DataSource(ABC):
    @abstractmethod
    def provide_files(self) -> Iterable[Tuple[str, ContentSupplier]]:
        pass


