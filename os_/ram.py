from os_.page import Page
from os_.config import PAGE_SIZE
from os_.synchronization import synchronized
from os_.sync_print import sync_print


class RAM:

    __slots__ = [
        'ram',
        'jobs_on_ram',
        'page_manager',
    ]

    DEFAULT_CAPACITY = 2 ** 10 // 4  # 1024 words

    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        self.ram: list = [
            Page()
            for i in range(capacity)
        ]
        self.jobs_on_ram = 0
        self.page_manager = None

    def __len__(self):
        return self.ram.__len__()

    def init_page_manager(self, page_manager):
        self.page_manager = page_manager
        for i in range(len(self.ram)):
            self.page_manager.add_page_to_pool(i)

    @synchronized
    def write_ram(self, address: int, page_data: Page):
        for i in range(PAGE_SIZE):
            self.ram[address].write_page(
                index=i,
                instruction=page_data.read_page(i)
            )
        self.page_manager.remove_page_to_pool(address)

    def read_ram(self, ram_address: int, page_address: int) -> str:
        return self.ram[ram_address].read_page(page_address)

    # -- Testing / Experimental -- #

    def print_ram(self, n = None):
        """     DEBUGGING   """
        c = 0
        for page in self.ram:
            for i in range(4):
                if n is not None and n < c:
                    return
                c += 1
                sync_print(page.read_page(i))
