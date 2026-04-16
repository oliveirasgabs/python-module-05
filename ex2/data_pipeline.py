from abc import ABC, abstractmethod
from typing import Any, Protocol


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


class ExportPlugin(Protocol):
    def process_output(self, data: list[tuple[int, str]]) -> None:
        ...


class CSVExportPlugin:
    def process_output(self, data: list[tuple[int, str]]) -> None:
        if not data:
            return
        csv_str = ",".join(val for rank, val in data)
        print(f"CSV Output:\n{csv_str}")


class JSONExportPlugin:
    def process_output(self, data: list[tuple[int, str]]) -> None:
        if not data:
            return
        items = [f'"item_{rank}": "{val}"' for rank, val in data]
        json_str = "{" + ", ".join(items) + "}"
        print(f"JSON Output:\n{json_str}")


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
        print("\n== DataStream statistics ==")
        if not self._processors:
            print("No processor found, no data")
            return
        for proc in self._processors:
            name: str = type(proc).__name__
            name = name.replace("Processor", " Processor")
            print(f"{name}: total {proc.total_processed()} items processed, "
                  f"remaining {proc.remaining()} on processor")

    def output_pipeline(self, nb: int, plugin: ExportPlugin) -> None:
        for proc in self._processors:
            to_export: list[tuple[int, str]] = []
            for _ in range(nb):
                try:
                    to_export.append(proc.output())
                except IndexError:
                    break
            if to_export:
                plugin.process_output(to_export)


def main() -> None:
    print("=== Code Nexus - Data Pipeline ===")

    print("\nInitialize Data Stream...")
    ds = DataStream()
    ds.print_processors_stats()

    print("\nRegistering Processors")
    ds.register_processor(NumericProcessor())
    ds.register_processor(TextProcessor())
    ds.register_processor(LogProcessor())

    batch1 = ['Hello world', [3.14, -1, 2.71],
              [{'log_level': 'WARNING',
                'log_message': 'Telnet access! Use ssh instead'},
               {'log_level': 'INFO',
                'log_message': 'User wil is connected'}], 42, ['Hi', 'five']]

    print(f"\nSend first batch of data on stream: {batch1}")
    ds.process_stream(batch1)
    ds.print_processors_stats()

    print("\nSend 3 processed data from each processor to a CSV plugin:")
    ds.output_pipeline(3, CSVExportPlugin())
    ds.print_processors_stats()

    print("\nSend another batch of data...")
    batch2 = [21,
              ['I love AI',
               'LLMs are wonderful',
               'Stay healthy'],
              [{'log_level': 'ERROR',
                'log_message': '500 server crash'},
               {'log_level': 'NOTICE',
                'log_message': 'Certificate expires in 10 days'}],
              [32, 42, 64, 84, 128, 168], 'World hello']

    ds.process_stream(batch2)
    ds.print_processors_stats()

    print("\nSend 5 processed data from each processor to a JSON plugin:")
    ds.output_pipeline(5, JSONExportPlugin())
    ds.print_processors_stats()


if __name__ == "__main__":
    main()
