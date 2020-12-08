from os_.kernel import Kernel
from os_.pcb import PCB
from os_.disk import Disk


class Loader:

    """
        Custom program file loader per CS3502 Project Specifications.
    """

    __slots__ = ['program_file', 'disk', 'kernel']

    def __init__(self, program_file: str, disk: Disk, kernel: Kernel):
        self.program_file = program_file
        self.disk = disk
        self.kernel = kernel
        # -- Variables -- #
        attributes = dict()
        words = list()
        # -- Iterate through program file -- #
        lines = self.open_program_file()
        while lines:
            line = lines.pop(0)
            if line.startswith('// JOB'):
                attributes['job_id'] = line.split()[-3]
                attributes['job_instr_count'] = int(line.split()[-2], 16)
                attributes['job_priority'] = line.split()[-1]
            elif line.startswith('// Data'):
                attributes['data_input_buffer'] = int(line.split()[-3], 16)
                attributes['data_output_buffer'] = int(line.split()[-2], 16)
                attributes['data_temp_buffer'] = int(line.split()[-1], 16)
            elif line.__contains__('END'):
                # -- Load Job -- #
                self.load_job(
                    {
                        'attributes': attributes,
                        'words': words,
                    }
                )
                # -- Reset Variables -- #
                attributes = dict()
                words = list()
            elif line.startswith('0x'):
                words.append(line)

    def load_job(self, job: dict):

        pcb = PCB(
            job_id=job['attributes']['job_id'],
            job_size=job['attributes']['job_instr_count'],
            priority=job['attributes']['job_priority'],
        )
        pcb.set_page_table(word_count=len(job['words']))
        pcb.set_disk_address_begin(address=self.disk.get_next_free_page())
        pcb.set_input_buffer(size=job['attributes']['data_input_buffer'])
        pcb.set_output_buffer(size=job['attributes']['data_output_buffer'])
        pcb.set_temp_buffer(size=job['attributes']['data_temp_buffer'])

        counter = 0
        for word in job['words']:
            n = self.disk.get_next_free_page()
            while self.disk.disk[n].is_index_free(counter % 4) is False:
                counter += 1
            self.disk.write_disk(
                page_num=n,
                index=counter % 4,
                instruction=word,
            )
            counter += 1
        self.kernel.add_pcb(pcb)

        # -- We want to make sure that all pages are relevant to the job. So if a jobs
        # -- words are complete prior to the last page being full, then just stop using
        # -- this page and move onto next page for next job.
        if self.disk.read_disk(self.disk.get_next_free_page()).get_words_available() != 4:
            pcb.set_disk_address_end(self.disk.get_next_free_page())
            self.disk.increment_next_free_page()
        else:
            pcb.set_disk_address_end(self.disk.get_next_free_page() - 1)

    def open_program_file(self) -> list:
        with open(self.program_file, 'r') as fh:
            return fh.read().splitlines()
