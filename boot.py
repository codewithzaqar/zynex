#!/usr/bin/env python3
"""Zynex Kernel Bootloader - v0.0.1a01"""

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
    mm = boot.kernel_instance.memory

    addr = mm.allocate(64)
    if addr is not None:
        mm.write(addr, b"Zynex v0.0.1a01")
        data = mm.read(addr, 15)
        print(f"  [TASK mem_demo] Read back: {data.decode()}")
        mm.free(addr)
        print(f"  [TASK mem_demo] Freed. Stats: {mm.stats()}")
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
