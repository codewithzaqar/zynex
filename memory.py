"""Zynex Memory Manager - Simple block allocator"""

from config import HEAP_SIZE_BYTES, DEBUG


class MemoryManager:
    def __init__(self):
        self._heap = bytearray(HEAP_SIZE_BYTES)
        self._allocations: dict[int, int] = {}  # addr -> size
        self._next_addr = 0
        self.total_allocated = 0

    def allocate(self, size: int) -> int | None:
        """Allocate a contiguous block, Returns address or None."""
        if size <= 0 or self._next_addr + size > HEAP_SIZE_BYTES:
            if DEBUG:
                print(f"[MEM] Allocation failed: requested={size}, available={HEAP_SIZE_BYTES - self._next_addr}")
            return None

        addr = self._next_addr
        self._allocations[addr] = size
        self._next_addr += size
        self.total_allocated += size
        return addr

    def free(self, addr: int) -> bool:
        """Free a previously allocated block."""
        if addr not in self._allocations:
            if DEBUG:
                print(f"[MEM] Invalid free at address {addr}")
            return False
        size = self._allocations.pop(addr)
        self.total_allocated -= size
        # NOTE: v0.0.1a uses bump allocator; freed blocks are NOT reused
        return True

    def read(self, addr: int, size: int) -> bytes:
        if addr not in self._allocations:
            raise MemoryError(f"Read from unallocated address {addr}")
        return bytes(self._heap[addr:addr + size])

    def write(self, addr: int, data: bytes) -> None:
        if addr not in self._allocations:
            raise MemoryError(f"Write to unallocated address {addr}")
        alloc_size = self._allocations[addr]
        if len(data) > alloc_size:
            raise MemoryError(f"Write overflow: {len(data)} > {alloc_size}")
        self._heap[addr:addr + len(data)] = data

    def stats(self) -> dict:
        return {
            "total_heap": HEAP_SIZE_BYTES,
            "allocated": self.total_allocated,
            "free": HEAP_SIZE_BYTES - self.total_allocated,
            "active_blocks": len(self._allocations),
        }
