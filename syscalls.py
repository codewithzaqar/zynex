"""Zynex Syscall Interface - v0.0.1a02"""

from enum import IntEnum
from typing import Any
from config import SYS_CALL_ENABLED


class SysCall(IntEnum):
    MEM_ALLOC = 1
    MEM_FREE = 2
    MEM_WRITE = 3
    MEM_READ = 4
    IPC_SEND = 10
    IPC_RECV = 11
    TASK_YIELD = 20
    CONSOLE_PRINT = 30


class SysCallResult:
    __slots__ = ("ok", "value", "error")

    def __init__(self, ok: bool, value: Any = None, error: str = ""):
        self.ok = ok
        self.value = value
        self.error = error

    def __repr__(self):
        return f"SysCallResult(ok={self.ok}, value={self.value!r})" if self.ok else f"SysCallResult(ERROR: {self.error})"


class SysCallHandler:
    """Mediates all user-task → kernel interactions."""

    def __init__(self, kernel):
        self._kernel = kernel

    def invoke(self, call: SysCall, *args) -> SysCallResult:
        if not SYS_CALL_ENABLED:
            return SysCallResult(False, error="Syscalls disabled in config")

        dispatch = {
            SysCall.MEM_ALLOC: self._mem_alloc,
            SysCall.MEM_FREE: self._mem_free,
            SysCall.MEM_WRITE: self._mem_write,
            SysCall.MEM_READ: self._mem_read,
            SysCall.CONSOLE_PRINT: self._console_print,
            SysCall.TASK_YIELD: self._task_yield,
        }

        handler = dispatch.get(call)
        if handler is None:
            return SysCallResult(False, error=f"Unknown syscall {call}")

        try:
            return handler(*args)
        except Exception as e:
            return SysCallResult(False, error=str(e))

    # --- Memory syscalls ---
    def _mem_alloc(self, size: int) -> SysCallResult:
        addr = self._kernel.memory.allocate(size)
        if addr is None:
            return SysCallResult(False, error="Out of memory")
        return SysCallResult(True, value=addr)

    def _mem_free(self, addr: int) -> SysCallResult:
        ok = self._kernel.memory.free(addr)
        return SysCallResult(ok, error="" if ok else "Invalid address")

    def _mem_write(self, addr: int, data: bytes) -> SysCallResult:
        self._kernel.memory.write(addr, data)
        return SysCallResult(True)

    def _mem_read(self, addr: int, size: int) -> SysCallResult:
        data = self._kernel.memory.read(addr, size)
        return SysCallResult(True, value=data)

    # --- Console syscall ---
    def _console_print(self, message: str) -> SysCallResult:
        tid = self._kernel.scheduler.current_task.tid if self._kernel.scheduler.current_task else -1
        self._kernel.console.print(f"[tid:{tid}] {message}", level="USER")
        return SysCallResult(True)

    # --- Scheduler syscall ---
    def _task_yield(self) -> SysCallResult:
        return SysCallResult(True)  # Yield handled by generator protocol
