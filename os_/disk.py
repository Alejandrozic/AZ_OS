from os_.page import Page
from os_.synchronization import synchronized
from os_.config import PAGE_SIZE


class Disk:

    __slots__ = [
        'disk',
        'jobs_on_disk',
        'next_free_page',
    ]

    DEFAULT_CAPACITY = 2 ** 11 // PAGE_SIZE  # 2048 words

    """
        Since in our implementation a page is tied 
        to a job, then we needed more pages to accommodate
        for the 'blank page slots' not used.
    """

    DEFAULT_CAPACITY += 400 // PAGE_SIZE  # words

    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        self.disk: list = [
            Page()
            for i in range(capacity)
        ]
        self.next_free_page = 0

    def __len__(self):
        """ Number of pages on disk"""
        return self.disk.__len__()

    @synchronized
    def write_disk(self, page_num: int, index: int, instruction: str):
        self.disk[page_num].write_page(index, instruction)
        if self.disk[page_num].is_full():
            self.increment_next_free_page()

    @synchronized
    def read_disk(self, page_num: int) -> Page:
        return self.disk[page_num]

    @synchronized
    def get_next_free_page(self) -> int:
        return self.next_free_page

    @synchronized
    def increment_next_free_page(self):
        self.next_free_page += 1
