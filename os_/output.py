import os
from os_.synchronization import synchronized


class Output:

    def __init__(self):
        self.path = os.path.abspath('.') + '/output'
        self.ram = None
        self.ram_dump_file = 'ram_dump.txt'
        self.ram_dump = list()
        self.disk_dump_file = 'disk_dump.txt'
        self.disk_dump = list()

    def save_to_file(self):
        with open(f'{self.path}/{self.ram_dump_file}', 'w') as fh:
            fh.write(f'// This is a frame based core dump of RAM.\n')
            fh.write(f'// Instructions are loaded into RAM as is\n')
            fh.write(f'// required by page faults. If page was not requested,\n')
            fh.write(f'// then you will see comment "Instruction Not LOADED in RAM".\n')
            fh.write(f'// We also included notations on where the input/temp/output buffers\n')
            fh.write(f'// and the instructions are located.\n')
            fh.write(f'\n')
            for line in self.ram_dump:
                fh.write(f'{line}\n')
        with open(f'{self.path}/{self.disk_dump_file}', 'w') as fh:
            fh.write(f'// This is a Dump of the Disk. The\n')
            fh.write(f'// None means that the word on the \n')
            fh.write(f'// Page was not used. This is because \n')
            fh.write(f'// we decided to have gaps and ensure\n')
            fh.write(f'// that each page is dedicated for only one job. \n')
            for line in self.disk_dump:
                fh.write(f'{line}\n')

    def set_ram(self, ram):
        self.ram = ram

    @synchronized
    def add_to_ram_dump(self, pcb, cpu_id: int):
        instruction_start = 0
        instruction_end = pcb.job_size - 1
        input_buffer_start = instruction_end + 1
        input_buffer_end = input_buffer_start + (pcb.len_input_buffer() - 1)
        output_buffer_start = input_buffer_end + 1
        output_buffer_end = output_buffer_start + (pcb.len_output_buffer() - 1)
        temp_buffer_start = output_buffer_end + 1
        temp_buffer_end = temp_buffer_start + (pcb.len_temp_buffer() - 1)
        counter = 0
        self.ram_dump.append(f'// JOB {pcb.job_id} [processed by cpu_{cpu_id}]')
        page_table = pcb.get_page_table()
        for x in range(len(page_table)):
            self.ram_dump.append(f'PAGE - {x}')
            ram_page = page_table.get_page(x)
            for y in range(4):
                if counter == instruction_start:
                    comment = 'INSTRUCTION START'
                elif counter == instruction_end:
                    comment = 'INSTRUCTION END'
                elif counter == input_buffer_start:
                    comment = 'INPUT BUFFER START'
                elif counter == input_buffer_end:
                    comment = 'INPUT BUFFER END'
                elif counter == output_buffer_start:
                    comment = 'OUTPUT BUFFER START'
                elif counter == output_buffer_end:
                    comment = 'OUTPUT BUFFER END'
                elif counter == temp_buffer_start:
                    comment = 'TEMP BUFFER START'
                elif counter == temp_buffer_end:
                    comment = 'TEMP BUFFER END'
                else:
                    comment = None
                if ram_page is not None:
                    data = self.ram.read_ram(ram_page, y)
                    if comment is None:
                        self.ram_dump.append(f' {data}')
                    else:
                        self.ram_dump.append(f' {data} ({comment})')
                else:
                    if comment is None:
                        self.ram_dump.append(f' Instruction Not LOADED in RAM')
                    else:
                        self.ram_dump.append(f' Instruction Not LOADED in RAM ({comment})')
                counter += 1
        self.ram_dump.append(f'\n')

    @synchronized
    def create_disk_dump(self, disk):
        for index in range(len(disk)):
            page = disk.read_disk(index)
            for i in range(4):
                self.disk_dump.append(page.read_page(i))
