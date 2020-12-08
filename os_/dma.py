from os_.ram import RAM
from os_.kernel import Kernel
from os_.logical_address import LogicalAddress
from os_.config import PAGE_SIZE
from os_.synchronization import synchronized
from os_.sync_print import sync_print

DMAChannelDEBUG = False


class DMAChannel:

    __slots__ = ['ram', 'kernel', '__is_running']

    def __init__(self, ram: RAM, kernel: Kernel):
        self.ram = ram
        self.kernel = kernel
        self.__is_running = True

    def start_daemon(self):
        while self.__is_running:
            if self.kernel.has_io_jobs():
                sync_print(
                    'DEBUG: [DMAChannel] Activated!'
                ) if DMAChannelDEBUG is True else None
                pcb = self.kernel.get_job_from_io_queue()
                logical_address = LogicalAddress()
                cached = self.kernel.get_pages_from_io_queue(pcb)
                for page_num in cached:
                    pcb.io_operations += 1
                    logical_address.set_page_number(page_num)
                    # -- get page table -- #
                    page_table = pcb.get_page_table()
                    # -- find page in ram -- #
                    ram_address = page_table.get_page(page_num)
                    # -- copy ram --> cache -- #
                    pcb_cache = pcb.cpu_state.get_cache()
                    for page_offset in range(PAGE_SIZE):
                        logical_address.set_page_offset(page_offset)
                        data = self.ram.read_ram(ram_address, page_address=page_offset)
                        pcb_cache.write_cache(logical_address, data)
                    # -- set valid/dirty bits -- #
                    pcb_cache.set_valid_page(page_num, True)
                    pcb_cache.set_dirty_page(page_num, False)
                # -- Completed, remove from queue -- #
                self.kernel.remove_from_io_queue(pcb)
                sync_print(
                    f'DEBUG: [DMAChannel] Ended with PID {pcb.job_id} state {pcb.state}'
                ) if DMAChannelDEBUG is True else None

    @synchronized
    def end_daemon(self):
        self.__is_running = False
