from os_.config import PAGE_SIZE


class LogicalAddress:

    def __init__(self, page_number: int = 0, page_offset: int = 0):
        self.page_number = page_number
        self.page_offset = page_offset

    def set_page_number(self, page_num: int):
        self.page_number = page_num

    def get_page_number(self) -> int:
        return self.page_number

    def set_page_offset(self, page_offset: int):
        self.page_offset = page_offset

    def get_page_offset(self) -> int:
        return self.page_offset

    def convert_from_raw_address(self, address: int):
        self.set_page_number(address // PAGE_SIZE)
        self.set_page_offset(address % PAGE_SIZE)
