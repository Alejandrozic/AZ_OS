import time
from os_.config import (
    NEW_STATE, READY_STATE, RUNNING_STATE, WAITING_STATE, ENDED_STATE,
)


class PCBStateMixin:

    def process_state_change(self, pcb, old_state: str, new_state: str):
        if old_state == READY_STATE and new_state == RUNNING_STATE:
            self.ready_to_running(pcb)
        elif old_state == RUNNING_STATE and new_state == WAITING_STATE:
            self.running_to_waiting(pcb)
        elif old_state == WAITING_STATE and new_state == READY_STATE:
            self.waiting_to_ready(pcb)
        elif old_state == RUNNING_STATE and new_state == ENDED_STATE:
            self.running_to_ended(pcb)
        elif old_state is None and new_state == NEW_STATE:
            # -- No stats here -- #
            pass
        elif old_state == NEW_STATE and new_state == READY_STATE:
            # -- No stats here -- #
            pass
        else:
            # -- Unexpected State -- #
            raise TypeError(f'[Statistics] Unexpected STATE change {old_state} -> {new_state}!')

    def ready_to_running(self, pcb):
        pcb.timer = time.time()

    def running_to_waiting(self, pcb):
        time_ran = time.time() - pcb.timer
        pcb.running_time += time_ran
        pcb.timer = time.time()

    def waiting_to_ready(self, pcb):
        waiting_time = time.time() - pcb.timer
        pcb.waiting_time += waiting_time
        pcb.timer = time.time()

    def running_to_ended(self, pcb):
        time_ran = time.time() - pcb.timer
        pcb.running_time += time_ran
        pcb.timer = None


class PercentageRAMUsedMixin:

    def process_percentage_ram_used(self, pcb, pages_in_ram: int):
        page_table = pcb.get_page_table()
        pages_used = 0
        for i in range(len(page_table)):
            ram_addr = page_table.get_page(i)
            if ram_addr is not None:
                pages_used += 1
        pcb.percent_ram_used = pages_used / pages_in_ram


class Statistics(PCBStateMixin, PercentageRAMUsedMixin):

    def __init__(self):
        self.report = list()
        self.report.append([
            'JOB_ID',
            'CPU_ID',
            'Running Time (R)',
            'Waiting Time (W)',
            'Completion Time (R + W)',
            'IO Operations',
            'Page Faults',
            'Ram used (%)',
        ])

    def save_to_report(self, pcb):
        self.report.append([
            pcb.job_id,
            pcb.assigned_cpu_id,
            round(pcb.running_time, ndigits=3),
            round(pcb.waiting_time, ndigits=3),
            round(pcb.running_time + pcb.waiting_time, ndigits=3),
            pcb.io_operations,
            pcb.page_fault_operations,
            round(pcb.percent_ram_used * 100, ndigits=2),
        ])

    def print_report(self):
        for line in self.report:
            print(','.join([str(i) for i in line]))
