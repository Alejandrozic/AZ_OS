import collections
from os_.pcb import PCB
from os_.synchronization import synchronized
from os_.sync_print import sync_print


class MemoryMapping:

    __slots__ = ['pcb_order', 'memory_map']

    def __init__(self):
        self.pcb_order = collections.deque()  # Linked List
        self.memory_map = dict()

    @synchronized
    def add_page_to_pcb(self, pcb: PCB, page_num: int):
        if pcb in self.memory_map:
            if page_num not in self.memory_map[pcb]:
                self.memory_map[pcb].append(page_num)
        else:
            self.pcb_order.append(pcb)
            page_nums = [page_num]
            self.memory_map[pcb] = page_nums

    @synchronized
    def get_pages_for_pcb(self, pcb: PCB) -> list:
        if pcb not in self.memory_map:
            raise UnexpectedMemoryMappingError('PCB not found!')
        tmp = self.memory_map[pcb]
        del self.memory_map[pcb]
        return tmp

    def contains(self, pcb: PCB) -> bool:
        return pcb in self.memory_map

    @synchronized
    def remove_from_queue(self, pcb: PCB):
        if pcb in self.pcb_order:
            self.pcb_order.remove(pcb)
        if pcb in self.memory_map:
            del self.memory_map[pcb]

    @synchronized
    def get_next_pcb(self) -> PCB:
        return self.pcb_order.popleft()

    def size(self) -> int:
        return self.pcb_order.__len__()

    def is_empty(self) -> bool:
        return len(self.memory_map) == 0


class UnexpectedMemoryMappingError(Exception):
    pass
