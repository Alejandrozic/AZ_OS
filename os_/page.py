from os_.config import PAGE_SIZE, EMPTY
from os_.synchronization import synchronized


class Page:

    __slots__ = [
        'page',
        'used',
    ]

    def __init__(self):
        """
            Initialize page as a list of elements.
            Set the number of words available to the size of the page.
            Set is_full boolean to False initially.
        """
        self.page: list = [EMPTY for i in range(PAGE_SIZE)]
        self.used = 0

    @synchronized
    def write_page(self, index: int, instruction: str):
        self.page[index] = instruction
        self.used += 1

    def read_page(self, index: int) -> str:
        return self.page[index]

    @synchronized
    def is_full(self) -> bool:
        return self.used == 4

    def get_words_available(self) -> int:
        return self.used

    def is_index_free(self, index: int) -> bool:
        return self.page[index] == EMPTY
