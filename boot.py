#!/usr/bin/env python3
"""Zynex Kernel Bootloader - v0.0.1a"""

from kernel import ZynexKernel
from ipc import Message


# --- Example user-space tasks ---

def hello_task():
    """Simple greeting task"""
    for i in range(5):
        print(f"  [TASK hello] Iteration {i}")
        yield  # Yield control back to scheduler


def counter_task(start: int = 0):
    """Counting task demonstrating parameterized coroutines"""
    count = start
    for _ in range(8):
        print(f"  [TASK counter] Count: {count}")
        count += 1
        yield


def memory_demo_task():
    """Demonstrates memory allocation within a task"""
    # Access kernel instance through a global or passed reference
    # For v0.0.1a01, we use a simple module-level reference
    import boot
    sc = boot.kernel_instance.syscall

    # Allocate via syscall
    result = sc.invoke(SysCall.MEM_ALLOC, 128)
    if not result.ok:
        sc.invoke(SysCall.CONSOLE_PRINT, f"Alloc failed: {result.error}")
        yield
        return

    addr = result.value
    sc.invoke(SysCall.MEM_WRITE, addr, b"Zynex v0.0.1a!")

    read_result = sc.invoke(SysCall.MEM_READ, addr, 16)
    sc.invoke(SysCall.CONSOLE_PRINT, f"Read back: {read_result.value.decode()}")

    # Free and re-allocate to prove free-list works (impossible in a)
    sc.invoke(SysCall.MEM_FREE, addr)
    result2 = sc.invoke(SysCall.MEM_ALLOC, 64)
    sc.invoke(SysCall.CONSOLE_PRINT, f"Re-alloc after free: addr=0x{result2.value:08X} (was 0x{addr:08X})")

    if result2.ok:
        sc.invoke(SysCall.MEM_FREE, result2.value)

    yield


# --- Boot sequence ---

if __name__ == "__main__":
    kernel_instance = ZynexKernel()
    kernel_instance.init()

    # Register tasks
    kernel_instance.scheduler.create_task("hello", hello_task)
    kernel_instance.scheduler.create_task("counter", counter_task, 100)
    kernel_instance.scheduler.create_task("mem_demo", memory_demo_task)

    # Start kernel with safety limit for alpha release
    kernel_instance.start(max_ticks=50)
