"""Zynex Scheduler - Round-robin cooperative multitasking"""

from collections import deque
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Any
from config import MAX_TASKS


class TaskState(Enum):
    READY = auto()
    RUNNING = auto()
    BLOCKED = auto()
    TERMINATED = auto()


@dataclass
class Task:
    tid: int
    name: str
    coroutine: Any  # Generator/coroutine object
    state: TaskState = TaskState.READY
    priority: int = 0
    metadata: dict = field(default_factory=dict)


class Scheduler:
    def __init__(self):
        self._ready_queue: deque[Task] = deque()
        self._tasks: dict[int, Task] = {}
        self._next_tid = 1
        self.current_task: Task | None = None
        self.tick_count = 0

    def create_task(self, name: str, coro_func: Callable, *args, priority: int = 0) -> int:
        if len(self._tasks) >= MAX_TASKS:
            raise RuntimeError(f"Max task limit ({MAX_TASKS}) reached")

        tid = self._next_tid
        self._next_tid += 1
        coroutine = coro_func(*args)
        task = Task(tid=tid, name=name, coroutine=coroutine, priority=priority)
        self._tasks[tid] = task
        self._ready_queue.append(task)
        return tid

    def terminate_task(self, tid: int) -> bool:
        task = self._tasks.get(tid)
        if task is None:
            return False
        task.state = TaskState.TERMINATED
        if task in self._ready_queue:
            self._ready_queue.remove(task)
        return True

    def tick(self) -> bool:
        """Execute one scheduling cycle. Returns False when no tasks remain."""
        # Remove terminated tasks
        self._ready_queue = deque(t for t in self._ready_queue if t.state != TaskState.TERMINATED)

        if not self._ready_queue:
            return False

        task = self._ready_queue.popleft()
        task.state = TaskState.RUNNING
        self.current_task = task
        self.tick_count += 1

        try:
            next(task.coroutine)
            if tas.state != TaskState.TERMINATED:
                task.state = TaskState.READY
                self._ready_queue.append(task)
        except StopIteration:
            task.state = TaskState.TERMINATED
        except Exception as e:
            print(f"[SCHED] Task '{task.name}' (tid={task.tid}) crashed: {e}")
            task.state = TaskState.TERMINATED

        self.current_task = None
        return True

    def active_count(self) -> int:
        return sum(1 for t in self._tasks.values() if t.state != TaskState.TERMINATED)
