"""Zynex Console Driver - Minimal stdout abstraction"""

import sys
from datetime import datetime


class ConsoleDriver:
    def __init__(self, prefix: str = "[ZYNEX]"):
        self.prefix = prefix
        self._buffer: list[str] = []

    def print(self, message: str, level: str = "INFO") -> None:
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        line = f"{timestamp} {self.prefix} [{level}] {message}"
        self._buffer.append(line)
        print(line, file=sys.stdout)

    def panic(self, message: str) -> None:
        self.print(message, level="PANIC")
        raise SystemExit(f"KERNEL PANIC: {message}")

    def get_log(self, last_n: int = 50) -> list[str]:
        return self._buffer[-last_n:]
