"""Zynex Memory Manager - Simple block allocator"""

from config import HEAP_SIZE_BYTES, DEBUG


class MemoryManager:
    def __init__(self):
        self._heap = bytearray(HEAP_SIZE_BYTES)
        # Free list: sorted list of (address, size) tuples
        self._free_list: list[tuple[int, int]] = [(0, HEAP_SIZE_BYTES)]
        self._allocations: dict[int, int] = {}  # addr -> size
        self.total_allocated = 0

    def allocate(self, size: int) -> int | None:
        """Allocate a contiguous block, Returns address or None."""
        if size <= 0:
            return None

        # Align to 8 bytes
        aligned_size = (size + 7) & ~7

        for i, (addr, block_size) in enumerate(self._free_list):
            if block_size >= aligned_size:
                # Found a fit
                self._allocations[addr] = aligned_size
                self.total_allocated += aligned_size

                remainder = block_size - aligned_size
                if remainder > 0:
                    self._free_list[i] = (addr + aligned_size, remainder)
                else:
                    self._free_list.pop(i)

                if DEBUG:
                    print(f"[MEM] Allocated {aligned_size}B @ 0x{addr:08X}")
                return addr

        if DEBUG:
            print(f"[MEM] OOM: requested={size}, largest_free={max((s for _, s in self._free_list), default=0)}")
        return None

    def free(self, addr: int) -> bool:
        """Free a previously allocated block."""
        if addr not in self._allocations:
            if DEBUG:
                print(f"[MEM] Invalid free @ 0x{addr:08X}")
            return False

        size = self._allocations.pop(addr)
        self.total_allocated -= size

        # Insert into free list maintaining sort order
        new_block = (addr, size)
        inserted = False
        for i, (faddr, fsize) in enumerate(self._free_list):
            if addr < faddr:
                self._free_list.insert(i, new_block)
                inserted = True
                break
        if not inserted:
            self._free_list.append(new_block)

        # Coalesce adjacent blocks
        self._coalesce()

        if DEBUG:
            print(f"[MEM] Freed {size}B @ 0x{addr:08X}, free_blocks={len(self._free_list)}")
        return True

    def _coalesce(self) -> None:
        """Merge adjacent free blocks."""
        merged = []
        for block in self._free_list:
            if merged and merged[-1][0] + merged[-1][1] == block[0]:
                prev_addr, prev_size = merged[-1]
                merged[-1] = (prev_addr, prev_size + block[1])
            else:
                merged.append(block)
        self._free_list = merged

    def read(self, addr: int, size: int) -> bytes:
        if addr not in self._allocations:
            raise MemoryError(f"Read from unallocated address {addr}")
        if size > self._allocations[addr]:
            raise MemoryError(f"Read overflow at 0x{addr:O8X}")
        return bytes(self._heap[addr:addr + size])

    def write(self, addr: int, data: bytes) -> None:
        if addr not in self._allocations:
            raise MemoryError(f"Write to unallocated address 0x{addr:08X}")
        if len(data) > self._allocations[addr]:
            raise MemoryError(f"Write overflow at 0x{addr:08X}")
        self._heap[addr:addr + len(data)] = data

    def stats(self) -> dict:
        largest = max((s for _, s in self._free_list), default=0)
        return {
            "total_heap": HEAP_SIZE_BYTES,
            "allocated": self.total_allocated,
            "free": HEAP_SIZE_BYTES - self.total_allocated,
            "active_blocks": len(self._allocations),
            "free_blocks": len(self._free_list),
            "largest_free": largest,
        }
