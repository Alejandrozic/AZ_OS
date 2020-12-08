import time
from os_.disk import Disk
from os_.ram import RAM
from os_.kernel import Kernel
from os_.page_manager import PageManager
from os_.loader import Loader
from os_.config import SCHEDULING_TYPE, CORE_DUMPS, statistics
from os_.longer_scheduler import LongScheduler
#from os_.short_scheduler_phase1 import ShortScheduler
from os_.short_scheduler_phase2 import ShortScheduler
from os_.sync_print import sync_print

OS_DRIVER_DEBUG = True


class OSDriver:

    def __init__(self, program_file: str):
        self.disk = Disk()
        self.ram = RAM()
        self.kernel = Kernel()
        self.page_manager = PageManager(
            disk=self.disk,
            kernel=self.kernel,
            ram=self.ram,
        )
        self.loader = Loader(
            disk=self.disk,
            kernel=self.kernel,
            program_file=program_file
        )
        sync_print('DEBUG: [OSDriver] __init__ completed.') if OS_DRIVER_DEBUG is True else None

    def run(self):
        start_time = time.time()
        if SCHEDULING_TYPE == 'FIFO':
            self.kernel.sort_by_fifo()
        elif SCHEDULING_TYPE == 'SJF':
            self.kernel.sort_by_shortest_job_first()
        elif SCHEDULING_TYPE == 'Priority':
            self.kernel.sort_by_priority()
        else:
            raise UnexpectedOSDriverError(f'Unsupported SCHEDULING_TYPE {SCHEDULING_TYPE}.')

        self.ram.init_page_manager(self.page_manager)

        CORE_DUMPS.set_ram(ram=self.ram)

        ls = LongScheduler(ram=self.ram, disk=self.disk, kernel=self.kernel)
        ls.run()

        sync_print(f'DEBUG: [OSDriver] LongScheduler loaded {self.kernel.get_queue_size()} jobs.') if OS_DRIVER_DEBUG is True else None

        ss = ShortScheduler(ram=self.ram, kernel=self.kernel, page_manager=self.page_manager)
        ss.run()

        sync_print('DEBUG: [OSDriver] ShortScheduler completed.') if OS_DRIVER_DEBUG is True else None

        # -- Waiting to finish -- #

        for cpu in ss.cpu_bank:
            while cpu.is_process_running() is True:
                pass
            sync_print(f'DEBUG: [OSDriver] CPU {cpu.cpu_id} completed {cpu.jobs_completed} jobs.') if OS_DRIVER_DEBUG is True else None

        sync_print(f'DEBUG: [OSDriver] Final in {round(time.time()-start_time, ndigits=2)}s.') if OS_DRIVER_DEBUG is True else None

        # -- Create the Disk Core Dump -- #
        CORE_DUMPS.create_disk_dump(self.disk)

        # -- Save the Core Dumps to file -- #
        CORE_DUMPS.save_to_file()

        # -- Print Stats Report -- #
        statistics.print_report()


class UnexpectedOSDriverError(Exception):
    pass
