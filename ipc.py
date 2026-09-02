"""Zynex IPC - Simple mailbox message passing"""

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any
from config import MESSAGE_QUEUE_SIZE


@dataclass(frozen=True)
class Message:
    sender_tid: int
    receiver_tid: int
    payload: Any
    tag: str = ""


class IPCManager:
    def __init__(self):
        self._mailboxes: dict[int, deque[Message]] = defaultdict(lambda: deque(maxlen=MESSAGE_QUEUE_SIZE))

    def send(self, msg: Message) -> bool:
        box = self._mailboxes[msg.receiver_tid]
        if len(box) >= MESSAGE_QUEUE_SIZE:
            return False  # Mailbox full
        box.append(msg)
        return True

    def receive(self, tid: int, blocking: bool = False) -> Message | None:
        box = self._mailboxes.get(tid)
        if box is None or len(box) == 0:
            return None
        return box.popleft()

    def pending(self, tid: int) -> int:
        return len(self._mailboxes.get(tid, []))
