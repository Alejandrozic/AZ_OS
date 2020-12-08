from os_.page import Page
from os_.logical_address import LogicalAddress
from os_.sync_print import sync_print
from os_.config import PAGE_SIZE


class Cache:

    # Largest job has 72 words, each page has 4 words,
    # such that having 18 cache indexes should be optimal.

    CACHE_SIZE = 72 // PAGE_SIZE

    def __init__(self):
        self.cache: list = [Page() for i in range(self.CACHE_SIZE)]
        self.valid: list = [False for i in range(self.CACHE_SIZE)]
        self.dirty: list = [False for i in range(self.CACHE_SIZE)]

    def set_valid_page(self, page_num: int, is_page_valid: bool):
        self.valid[page_num] = is_page_valid

    def set_dirty_page(self, page_num: int, is_dirty_page: bool):
        self.dirty[page_num] = is_dirty_page

    def read_page(self, page_num: int) -> Page:
        return self.cache[page_num]

    def read_cache(self, logical_address: LogicalAddress) -> str:
        page_num = logical_address.get_page_number()
        page_offset = logical_address.get_page_offset()
        return self.cache[page_num].read_page(index=page_offset)

    def write_cache(self, logical_address: LogicalAddress, data: str):
        page_num = logical_address.get_page_number()
        offset = logical_address.get_page_offset()
        self.cache[page_num].write_page(index=offset, instruction=data)
        self.set_dirty_page(page_num, is_dirty_page=True)

    def is_page_valid(self, **kwargs) -> bool:
        logical_address: LogicalAddress = kwargs.get('logical_address', None)
        index = kwargs.get('index', None)
        try:
            return self.valid[index]
        except TypeError:
            pass
        try:
            return self.valid[logical_address.get_page_number()]
        except TypeError:
            pass
        raise UnexpectedCacheError('Parameter is required!')

    def is_page_modified(self, **kwargs):
        logical_address: LogicalAddress = kwargs.get('logical_address', None)
        index = kwargs.get('index', None)
        try:
            return self.dirty[index]
        except TypeError:
            pass
        try:
            return self.dirty[logical_address.get_page_number()]
        except TypeError:
            pass
        raise UnexpectedCacheError('Parameter is required!')

    def print_cache(self):
        """     Troubleshooting     """
        sync_print('------------------------------')
        for page in self.cache:
            for i in range(4):
                sync_print(page.page[i])
        sync_print('------------------------------')


class UnexpectedCacheError(Exception):
    pass
