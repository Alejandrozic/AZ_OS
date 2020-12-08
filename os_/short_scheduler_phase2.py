import threading
from os_.ram import RAM
from os_.kernel import Kernel
from os_.page_manager import PageManager
from os_.config import CPU_COUNT, READY_STATE, RUNNING_STATE, WAITING_STATE, ENDED_STATE, CORE_DUMPS, statistics
from os_.dma import DMAChannel
from os_.mmu import MMU
from os_.cpu import CPU


class ShortScheduler:

    def __init__(self, ram: RAM, kernel: Kernel, page_manager: PageManager):
        self.ram = ram
        self.kernel = kernel

        self.dma = DMAChannel(ram=self.ram, kernel=self.kernel)
        threading.Thread(target=self.dma.start_daemon, args=(), daemon=True).start()

        self.page_manager = page_manager
        threading.Thread(target=self.page_manager.start_daemon, args=(), daemon=True).start()

        self.mmu = MMU(kernel=self.kernel, ram=self.ram)

        self.cpu_bank = list()
        id_num_offset = 1
        for i in range(id_num_offset, CPU_COUNT + id_num_offset):
            cpu = CPU(id_=i, mmu=self.mmu)
            self.cpu_bank.append(cpu)
            threading.Thread(target=cpu.run, args=(), daemon=True).start()

    def run(self):
        threads = list()
        for i in range(CPU_COUNT):
            t = threading.Thread(target=self.dispatcher, args=(self.cpu_bank[i],))
            t.start()
            threads.append(t)

        for index, thread in enumerate(threads):
            thread.join()

        self.page_manager.end_daemon()
        self.dma.end_daemon()

    def dispatcher(self, cpu: CPU):
        while self.kernel.get_queue_size() > 0:
            next_job = self.kernel.get_next_pcb(cpu_id=cpu.cpu_id)

            if next_job is None:
                continue

            next_job.assigned_cpu_id = cpu.cpu_id

            while cpu.is_process_running():
                pass

            if next_job.get_state() == READY_STATE:
                next_job.set_state(RUNNING_STATE)
                cpu.run_pcb(next_job)

            elif next_job.get_state() == WAITING_STATE:
                if not self.kernel.io_queue.contains(next_job) and \
                        not self.kernel.page_fault_queue.contains(pcb=next_job):
                    next_job.set_state(READY_STATE)

            elif next_job.get_state() == ENDED_STATE:
                CORE_DUMPS.add_to_ram_dump(pcb=next_job, cpu_id=cpu.cpu_id)
                statistics.process_percentage_ram_used(
                    pcb=next_job,
                    pages_in_ram=len(self.ram)
                )
                statistics.save_to_report(pcb=next_job)
                self.page_manager.clean_page_table(pcb=next_job)
                self.kernel.pcb_queue.remove(next_job)
