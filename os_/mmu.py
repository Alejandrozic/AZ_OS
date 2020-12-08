from os_.ram import RAM
from os_.kernel import Kernel
from os_.cache import Cache
from os_.logical_address import LogicalAddress
from os_.pcb import PCB
from os_.config import WAITING_STATE
from os_.synchronization import synchronized
from os_.sync_print import sync_print


MMU_DEBUG = False


class MMU:

    __slots__ = ['kernel', 'ram']

    def __init__(self, kernel: Kernel, ram: RAM):
        self.kernel = kernel
        self.ram = ram

    @synchronized
    def check_for_interrupt(self, logical_address: LogicalAddress, cache: Cache, pcb: PCB) -> bool:
        is_interrupt = False
        page_num = logical_address.get_page_number()
        if cache.is_page_valid(logical_address=logical_address) is False:
            if pcb.get_page_table().is_valid(page_num) is False:
                sync_print('DEBUG: [MMU] Page Fault.') if MMU_DEBUG is True else None
                self.kernel.add_to_page_fault_queue(pcb, page_num)
            else:
                sync_print('DEBUG: [MMU] IO Queue.') if MMU_DEBUG is True else None
                self.kernel.add_to_io_queue(pcb, page_num)
            pcb.set_state(WAITING_STATE)
            is_interrupt = True
        return is_interrupt

    @synchronized
    def write_to_ram(self, pcb: PCB):
        cache = pcb.cpu_state.get_cache()
        page_table = pcb.page_table
        for i in range(cache.CACHE_SIZE):
            if cache.is_page_modified(index=i) and cache.is_page_valid(index=i):
                ram_address = page_table.get_page(page_num=i)
                self.ram.write_ram(ram_address, cache.read_page(page_num=i))

    @staticmethod
    @synchronized
    def read_cache(logical_address: LogicalAddress, cache: Cache) -> str:
        return cache.read_cache(logical_address)

    @staticmethod
    @synchronized
    def write_cache(logical_address: LogicalAddress, data: str, cache: Cache):
        cache.write_cache(logical_address, data)
