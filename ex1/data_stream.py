from abc import ABC, abstractmethod
from typing import Any


class DataProcessor(ABC):
    def __init__(self) -> None:
        self._buffer: list[tuple[int, str]] = []
        self._processing_rank: int = 0
        self._total_processed: int = 0

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

    def total_processed(self) -> int:
        return self._total_processed

    def remaining(self) -> int:
        return len(self._buffer)


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
                self._total_processed += 1
        else:
            self._buffer.append((self._processing_rank, str(data)))
            self._processing_rank += 1
            self._total_processed += 1


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
                self._total_processed += 1
        else:
            self._buffer.append((self._processing_rank, data))
            self._processing_rank += 1
            self._total_processed += 1


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
                self._total_processed += 1
        else:
            log_str = ": ".join(data.values())
            self._buffer.append((self._processing_rank, log_str))
            self._processing_rank += 1
            self._total_processed += 1


class DataStream:
    def __init__(self) -> None:
        self._processors: list[DataProcessor] = []

    def register_processor(self, proc: DataProcessor) -> None:
        self._processors.append(proc)

    def process_stream(self, stream: list[Any]) -> None:
        for element in stream:
            handled: bool = False
            for proc in self._processors:
                if proc.validate(element):
                    proc.ingest(element)
                    handled = True
                    break
            if not handled:
                print(f"DataStream error - Can't process "
                      f"element in stream: {element}")

    def print_processors_stats(self) -> None:
        print("== DataStream statistics ==")
        if not self._processors:
            print("No processor found, no data")
            return
        for proc in self._processors:
            name: str = type(proc).__name__
            name = name.replace("Processor", " Processor")
            print(f"{name}: total {proc.total_processed()} items processed, "
                  f"remaining {proc.remaining()} on processor")


def main() -> None:
    print("=== Code Nexus - Data Stream ===")
    print("Initialize Data Stream...")
    ds: DataStream = DataStream()
    ds.print_processors_stats()

    print("\nRegistering Numeric Processor")
    num_proc: NumericProcessor = NumericProcessor()
    ds.register_processor(num_proc)

    batch: list[Any] = [
        'Hello world',
        [3.14, -1, 2.71],
        [
            {'log_level': 'WARNING',
             'log_message': 'Telnet access! Use ssh instead'},
            {'log_level': 'INFO',
             'log_message': 'User wil is connected'}
        ],
        42,
        ['Hi', 'five']
    ]

    print("Send first batch of data on stream:", batch)
    ds.process_stream(batch)
    ds.print_processors_stats()

    print("\nRegistering other data processors")
    text_proc: TextProcessor = TextProcessor()
    log_proc: LogProcessor = LogProcessor()
    ds.register_processor(text_proc)
    ds.register_processor(log_proc)

    print("Send the same batch again")
    ds.process_stream(batch)
    ds.print_processors_stats()

    print("\nConsume some elements from the data "
          "processors: Numeric 3, Text 2, Log 1")
    for _ in range(3):
        num_proc.output()
    for _ in range(2):
        text_proc.output()
    for _ in range(1):
        log_proc.output()

    ds.print_processors_stats()


if __name__ == "__main__":
    main()
