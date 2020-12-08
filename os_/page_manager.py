from os_.ram import RAM
from os_.disk import Disk
from os_.pcb import PCB
from os_.kernel import Kernel
from os_.synchronization import synchronized
from os_.sync_print import sync_print

PageManagerDEBUG = False


class PageManager:

    __slots__ = [
        'kernel',
        'ram',
        'disk',
        '__is_running',
        'free_page_pool',
    ]

    def __init__(self, kernel: Kernel, ram: RAM, disk: Disk):
        self.kernel = kernel
        self.ram = ram
        self.disk = disk
        self.__is_running = True
        self.free_page_pool = list()

    @synchronized
    def add_page_to_pool(self, page_num: int):
        if page_num not in self.free_page_pool:
            self.free_page_pool.append(page_num)

    @synchronized
    def remove_page_to_pool(self, page_num: int):
        if page_num in self.free_page_pool:
            self.free_page_pool.remove(page_num)

    @synchronized
    def clean_page_table(self, pcb: PCB):
        for i in range(pcb.page_table.table.__len__()):
            ram_page = pcb.page_table.table[i]
            if ram_page is not None:
                self.add_page_to_pool(page_num=ram_page)
                pcb.page_table.flip_valid(page_num=i)

    def is_page_available(self) -> bool:
        return self.free_page_pool.__len__() > 0

    def start_daemon(self):
        while self.__is_running is True:
            # -- Continue Here -- #
            if self.kernel.has_page_fault_jobs() is True and self.is_page_available() is True:
                sync_print('DEBUG: [Page Manager] Activated!') if PageManagerDEBUG is True else None
                pcb: PCB = self.kernel.get_job_from_page_fault_queue()
                page_faults: list = self.kernel.get_pages_from_page_fault_queue(pcb)
                for page_num in page_faults:
                    pcb.page_fault_operations += 1
                    disk_index = pcb.get_disk_address_begin() + page_num
                    page_index = self.free_page_pool.pop(0)
                    self.ram.write_ram(address=page_index, page_data=self.disk.read_disk(disk_index))
                    pcb.get_page_table().write_page_table(page_num=page_num, ram_address=page_index)
                self.kernel.remove_from_page_fault_queue(pcb)
                sync_print('DEBUG: [Page Manager] Ended!') if PageManagerDEBUG is True else None

    @synchronized
    def end_daemon(self):
        self.__is_running = False
