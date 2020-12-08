from os_.page_table import PageTable
from os_.page import Page
from os_.cpu_state import CPUState
from os_.config import (
    SCHEDULING_TYPE,
    NEW_STATE,
    PAGE_SIZE,
    statistics,
)
from os_.synchronization import synchronized
from os_.sync_print import sync_print

PCB_DEBUG = False


class PCB:

    __slots__ = [
        'job_id', 'job_size', 'priority', 'page_table',
        'input_buffer', 'output_buffer', 'temp_buffer', 'state',
        'cpu_state', 'disk_address_begin', 'disk_address_end', 'assigned_cpu_id',
        'timer', 'waiting_time', 'running_time', 'io_operations', 'percent_ram_used',
        'page_fault_operations',
    ]

    def __init__(self, job_id: str, job_size: int, priority: int):
        # -- Initialized and NOT changed -- #
        self.job_id = job_id
        self.job_size = job_size
        self.priority = priority
        self.page_table = None
        self.input_buffer = list()
        self.output_buffer = list()
        self.temp_buffer = list()

        # -- Initialized and LATER changed -- #
        self.state = None
        self.set_state(NEW_STATE)
        self.cpu_state = CPUState()
        self.disk_address_begin = 0
        self.disk_address_end = None

        # -- CPU ID Persistence -- #
        self.assigned_cpu_id = None

        # -- Stats -- #
        self.timer = 0.0
        self.waiting_time = 0.0
        self.running_time = 0.0
        self.io_operations = 0
        self.page_fault_operations = 0
        self.percent_ram_used = 0.0

    def __hash__(self):
        """
            Implements hashing functionality to on a Python PCB Object. This
            is useful when using object as a key on a dictionary.
        """
        return hash(f'{self.job_id},{self.job_size},{self.priority}')

    def __lt__(self, other) -> bool:
        """     Implements Less Then or Equal to on a Python PCB Object     """
        if SCHEDULING_TYPE == 'SJF':
            return self.job_size < other.job_size
        elif SCHEDULING_TYPE == 'Priority':
            return self.priority < other.priority
        elif SCHEDULING_TYPE == 'FIFO':
            return self.job_id < other.job_id

    def __eq__(self, other) -> bool:
        """     Implements Equal to on a Python PCB Object     """
        return self.job_id == other.job_id

    # --------------- #
    # -- State     -- #
    # --------------- #

    def get_state(self) -> str:
        return self.state

    @synchronized
    def set_state(self, state: str):
        statistics.process_state_change(pcb=self, old_state=self.state, new_state=state)
        self.state = state
        sync_print(f'DEBUG: STATE {self.state} PID {self.job_id}') if PCB_DEBUG is True else None

    # --------------- #
    # -- CPU STATE -- #
    # --------------- #

    def get_cpu_state(self) -> CPUState:
        return self.cpu_state

    @synchronized
    def set_cpu_state(self, state: CPUState):
        self.cpu_state = state

    # ------------- #
    # -- BUFFERS -- #
    # ------------- #

    def get_input_buffer(self) -> list:
        return self.input_buffer

    def get_temp_buffer(self) -> list:
        return self.temp_buffer

    def get_output_buffer(self) -> list:
        return self.output_buffer

    @synchronized
    def set_input_buffer(self, size: int):
        i = 0
        while size / 4 > i:
            self.input_buffer.append(Page())
            i += 1

    @synchronized
    def set_output_buffer(self, size: int):
        i = 0
        while size / 4 > i:
            self.output_buffer.append(Page())
            i += 1

    @synchronized
    def set_temp_buffer(self, size: int):
        i = 0
        while size / 4 > i:
            self.temp_buffer.append(Page())
            i += 1

    def len_temp_buffer(self) -> int:
        return len(self.temp_buffer) * PAGE_SIZE

    def len_output_buffer(self) -> int:
        return len(self.output_buffer) * PAGE_SIZE

    def len_input_buffer(self) -> int:
        return len(self.input_buffer) * PAGE_SIZE

    # -------------------------------- #
    # -- Page Table                 -- #
    # -- object initialized once,   -- #
    # -- so no set is required.     -- #
    # -------------------------------- #

    def get_page_table(self) -> PageTable:
        return self.page_table

    @synchronized
    def set_page_table(self, word_count: int):
        page_count = word_count // 4
        if word_count % 4 > 0:
            page_count += 1
        self.page_table = PageTable(page_count=page_count)

    # ---------- #
    # -- DISK -- #
    # ---------- #

    def get_disk_address_begin(self) -> int:
        return self.disk_address_begin

    def get_disk_address_end(self) -> int:
        return self.disk_address_end

    def set_disk_address_begin(self, address: int):
        self.disk_address_begin = address

    def set_disk_address_end(self, address: int):
        self.disk_address_end = address
