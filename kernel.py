"""Zynex Kernel Core - Orchestrates all subsystems"""

import traceback
from syscalls import SysCallHandler, SysCall
from config import VERSION, CODENAME, TICK_RATE_HZ
from memory import MemoryManager
from scheduler import Scheduler
from ipc import IPCManager, Message
from drivers.console import ConsoleDriver


class ZynexKernel:
    def __init__(self):
        self.console = ConsoleDriver()
        self.memory = MemoryManager()
        self.scheduler = Scheduler()
        self.ipc = IPCManager()
        self.running = False
        self.syscall = SysCallHandler(self)

    def init(self) -> None:
        self.console.print(f"Zynex Kernel v{VERSION} ({CODENAME}) initializing...")
        self.console.print(f"Memory: {self.memory.stats()}")
        self.console.print(f"Tick rate: {TICK_RATE_HZ} Hz")
        self.console.print("All subsystems initialized successfully.", level="OK")

    def start(self, max_ticks: int | None = None) -> None:
        self.running = True
        self.console.print("Kernel started. Entering main loop.")
        ticks = 0

        try:
            while self.running:
                has_tasks = self.scheduler.tick()
                ticks += 1

                if max_ticks and ticks >= max_ticks:
                    self.console.print(f"Max ticks ({max_ticks}) reached. Halting.")
                    break

                if not has_tasks:
                    self.console.print("No active tasks. Kernel idle.", level="IDLE")
                    break
        except KeyboardInterrupt:
            self.console.print("Interrupt received. Shutting down.", level="WARN")
        finally:
            self.shutdown()

    def panic(self, messgae: str, exc: Exception | None = None) -> None:
        self.console.print(f"KERNEL PANIC: {message}", level="PANIC")
        if exc and PANIC_DUMP_STACK:
            tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            for line in tb.strip().split("\n"):
                self.console.print(f" {line}", level="TRACE")
        self.running = False
        self.shutdown()

    def shutdown(self) -> None:
        self.running = False
        self.console.print(f"Final stats: ticks={self.scheduler.tick_count}, "
                           f"memory={self.memory.stats()}, "
                           f"active_tasks={self.scheduler.active_count()}")
        self.console.print("Zynex Kernel halted.", level="OK")
