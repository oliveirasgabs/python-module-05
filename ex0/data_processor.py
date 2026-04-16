from abc import ABC, abstractmethod
from typing import Any


class DataProcessor(ABC):
    def __init__(self) -> None:
        self._buffer: list[tuple[int, str]] = []
        self._processing_rank: int = 0

    @abstractmethod
    def validate(self, data: Any) -> bool:
        pass

    @abstractmethod
    def ingest(self, data: Any) -> None:
        pass

    def output(self) -> tuple[int, str]:
        if not self._buffer:
            raise IndexError("Buffer is empty")
        return self._buffer.pop(0)


class NumericProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        if isinstance(data, int | float):
            return True
        elif isinstance(data, list) and all(
                isinstance(i, int | float) for i in data):
            return True
        else:
            return False

    def ingest(self, data: int | float | list[int | float]) -> None:
        if not self.validate(data):
            raise TypeError("Improper numeric data")
        if isinstance(data, list):
            for item in data:
                self._buffer.append((self._processing_rank, str(item)))
                self._processing_rank += 1
        else:
            self._buffer.append((self._processing_rank, str(data)))
            self._processing_rank += 1


class TextProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        if isinstance(data, str):
            return True
        elif isinstance(data, list) and all(isinstance(i, str) for i in data):
            return True
        else:
            return False

    def ingest(self, data: str | list[str]) -> None:
        if not self.validate(data):
            raise TypeError("Improper text data")
        if isinstance(data, list):
            for item in data:
                self._buffer.append((self._processing_rank, item))
                self._processing_rank += 1
        else:
            self._buffer.append((self._processing_rank, data))
            self._processing_rank += 1


class LogProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        if isinstance(data, dict) and all(
                isinstance(k, str) and isinstance(
                    v, str) for k, v in data.items()):
            return True
        elif isinstance(data, list) and all(
                isinstance(i, dict) and all(
                    isinstance(k, str) and isinstance(
                        v, str) for k, v in i.items()) for i in data):
            return True
        else:
            return False

    def ingest(self, data: dict[str, str] | list[dict[str, str]]) -> None:
        if not self.validate(data):
            raise TypeError("Improper log data")
        if isinstance(data, list):
            for key in data:
                log_str: str = ": ".join(key.values())
                self._buffer.append((self._processing_rank, log_str))
                self._processing_rank += 1
        else:
            log_str = ": ".join(data.values())
            self._buffer.append((self._processing_rank, log_str))
            self._processing_rank += 1


def main() -> None:

    print("=== Code Nexus - Data Processor ===\n")
    print("Testing Numeric Processor...")
    num_processor: NumericProcessor = NumericProcessor()
    print(f"Trying to validate input '42': {num_processor.validate(42)}")
    print(f"Trying to validate input 'Hello': "
          f"{num_processor.validate('Hello')}")

    try:
        print("Test invalid ingestion of string "
              "'foo' without prior validation:")
        num_processor.ingest("foo")
    except TypeError as error:
        print(f"Got exception: {error}")

    # try:
    #     print("\nTest invalid ingestion of string "
    #           "'None' without prior validation:")
    #     num_processor.ingest(None)
    # except TypeError as error:
    #     print(f"Got exception: {error}")

    num_data: list[int | float] = [1, 2, 3, 4, 5]
    print(f"Processing data: {num_data}")
    num_processor.ingest(num_data)
    print("Extracting 3 values...")
    for _ in range(3):
        i: int
        value: str
        i, value = num_processor.output()
        print(f"Numeric value {i}: {value}")

    # empty_list: list[int] = []
    # print(f"\nTrying to validate empty list: "
    #       f"{num_processor.validate(empty_list)}")
    # print("\nTrying to ingest empty list:")
    # try:
    #     num_processor.ingest(empty_list)
    #     num_processor.output()
    # except IndexError as error:
    #     print(f"Got exception: {error}")

    print("\nTesting Text Processor...")
    text_proc: TextProcessor = TextProcessor()
    text_data: list[str] = ['Hello', 'Nexus', 'World']
    print(f"Processing data: {text_data}")
    text_proc.ingest(text_data)
    i, value = text_proc.output()
    print(f"Extracting 1 value...\nText value {i}: {value}")

    print("\nTesting Log Processor...")
    log_proc: LogProcessor = LogProcessor()
    log_data: list[dict[str, str]] = [
        {'log_level': 'NOTICE', 'log_message': 'Connection to server'},
        {'log_level': 'ERROR', 'log_message': 'Unauthorized access!!'}
    ]
    print(f"Processing data: {log_data}")
    log_proc.ingest(log_data)

    print("Extracting 2 values...")
    for _ in range(2):
        i, value = log_proc.output()
        print(f"Log entry {i}: {value}")


if __name__ == "__main__":
    main()
