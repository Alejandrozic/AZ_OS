from heapq import heappush, heappop
from os_.memory_mapping import MemoryMapping
from os_.pcb import PCB
from os_.config import RUNNING_STATE
from os_.synchronization import synchronized
from os_.sync_print import sync_print


class Kernel:

    __slots__ = ['pcb_queue', 'page_fault_queue', 'io_queue']

    def __init__(self):
        self.pcb_queue = list()
        self.page_fault_queue = MemoryMapping()
        self.io_queue = MemoryMapping()

    @synchronized
    def sort_by_fifo(self):
        heap = list()
        while self.pcb_queue:
            pcb = self.pcb_queue.pop(0)
            heappush(heap, (int(pcb.job_id, 16), pcb))
        while heap:
            pos, pcb = heappop(heap)
            self.pcb_queue.append(pcb)

    @synchronized
    def sort_by_priority(self):
        heap = list()
        while self.pcb_queue:
            pcb = self.pcb_queue.pop(0)
            heappush(heap, (int(pcb.priority, 16), pcb))
        while heap:
            pos, pcb = heappop(heap)
            self.pcb_queue.append(pcb)

    @synchronized
    def sort_by_shortest_job_first(self):
        heap = list()
        while self.pcb_queue:
            pcb = self.pcb_queue.pop(0)
            heappush(heap, (pcb.job_size, pcb))
        while heap:
            pos, pcb = heappop(heap)
            self.pcb_queue.append(pcb)

    @synchronized
    def get_pcb(self, index: int) -> PCB:
        return self.pcb_queue[index]

    @synchronized
    def get_next_pcb(self, cpu_id: int) -> PCB:
        for pcb in self.pcb_queue:
            if pcb.get_state() != RUNNING_STATE:
                if pcb.assigned_cpu_id is None or pcb.assigned_cpu_id == cpu_id:
                    return pcb

    @synchronized
    def add_pcb(self, pcb: PCB):
        self.pcb_queue.append(pcb)

    @synchronized
    def add_to_page_fault_queue(self, pcb: PCB, page_num: int):
        self.page_fault_queue.add_page_to_pcb(pcb, page_num)

    @synchronized
    def get_job_from_page_fault_queue(self) -> PCB:
        return self.page_fault_queue.get_next_pcb()

    @synchronized
    def get_pages_from_page_fault_queue(self, pcb: PCB) -> list:
        return self.page_fault_queue.get_pages_for_pcb(pcb)

    @synchronized
    def remove_from_page_fault_queue(self, pcb: PCB):
        self.page_fault_queue.remove_from_queue(pcb)

    @synchronized
    def add_to_io_queue(self, pcb: PCB, page_num: int):
        self.io_queue.add_page_to_pcb(pcb, page_num)

    @synchronized
    def get_job_from_io_queue(self) -> PCB:
        return self.io_queue.get_next_pcb()

    @synchronized
    def get_pages_from_io_queue(self, pcb: PCB) -> list:
        return self.io_queue.get_pages_for_pcb(pcb)

    @synchronized
    def remove_from_io_queue(self, pcb: PCB):
        self.io_queue.remove_from_queue(pcb)

    def has_page_fault_jobs(self) -> bool:
        return self.page_fault_queue.size() > 0

    def has_io_jobs(self) -> bool:
        return self.io_queue.size() > 0

    def get_queue_size(self) -> int:
        return len(self.pcb_queue)

    def get_page_fault_size(self) -> int:
        return self.page_fault_queue.size()

    def get_io_queue_size(self) -> int:
        return self.io_queue.size()
