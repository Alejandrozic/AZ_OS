from os_.synchronization import synchronized
from os_.sync_print import sync_print


class PageTable:

    __slots__ = ['page_count', 'table', 'valid_bits']

    def __init__(self, page_count: int):
        self.page_count: int = page_count
        self.table: list = [None for i in range(page_count)]
        self.valid_bits: list = [False for i in range(page_count)]

    def __len__(self):
        return self.page_count

    @synchronized
    def write_page_table(self, page_num: int, ram_address: int):
        self.table[page_num] = ram_address
        self.valid_bits[page_num] = True

    def read_page_table(self) -> list:
        return self.table

    @synchronized
    def get_page(self, page_num: int) -> int:
        return self.table[page_num]

    @synchronized
    def is_valid(self, page_num: int) -> bool:
        return self.valid_bits[page_num]

    @synchronized
    def flip_valid(self, page_num: int):
        self.valid_bits[page_num] = not self.valid_bits[page_num]

    def print_page_table(self):
        sync_print('-----------------------')
        for i in range(self.page_count):
            sync_print(f'table page_num {i} -> ram_addr {self.table[i]}')
        sync_print('-----------------------')
