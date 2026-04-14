from abc import ABC, abstractmethod
from typing import Any


class DataProcessor(ABC):
    def __init__(self):
        buffer: list[Any] = []

    @abstractmethod
    def validate(self, data: Any) -> bool:
        pass
    
    @abstractmethod
    def ingest(self, data: Any) -> None:
        pass

    def output(self) -> tuple[int, str]:
        return [numeric: int, string: str]
    pass


class NumericProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        if isinstance(data, int | float | list[int | float]):
            
            return True
        else:
            raise TypeError("Improper numeric data")

    def ingest(self, data: int | float | list[int | float]):

        return super().ingest()


class TextProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        if isinstance(data, str):
        return

    def ingest(self, data: str | list[str]):
        return


class LogProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        return

    def ingest(self, data: dict{}):
        return
