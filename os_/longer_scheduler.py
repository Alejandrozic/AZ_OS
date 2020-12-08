from os_.ram import RAM
from os_.disk import Disk
from os_.kernel import Kernel
from os_.config import PAGE_SIZE, READY_STATE


class LongScheduler:

    def __init__(self, ram: RAM, disk: Disk, kernel: Kernel):
        self.ram = ram
        self.disk = disk
        self.kernel = kernel
        self.ram_page_counter = 0

    def run(self):
        # -- for each pcb -- #
        for pcb_cnt in range(self.kernel.get_queue_size()):
            pcb = self.kernel.get_pcb(pcb_cnt)
            # - write first 4 pages (16 words) -- #
            for page_index in range(PAGE_SIZE):
                self.ram.write_ram(
                    address=self.ram_page_counter,
                    page_data=self.disk.read_disk(
                        pcb.get_disk_address_begin() + page_index
                    ),
                )
                # -- add job to page table -- #
                pcb.get_page_table().write_page_table(
                    page_num=page_index,
                    ram_address=self.ram_page_counter
                )
                # -- add one to ram_loc which keeps track of virtual ram index -- #
                self.ram_page_counter += 1
            # -- set pcb to ready state -- #
            pcb.set_state(READY_STATE)
