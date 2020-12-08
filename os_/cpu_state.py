from os_.instruction import Instruction
from os_.cache import Cache
from os_.synchronization import synchronized


class CPUState:

    __slots__ = [
        'pc',
        'instruction',
        'registers',
        'cache',
    ]

    REGISTER_COUNT = 16

    def __init__(self):
        self.pc = 0
        self.instruction = Instruction()
        self.registers: list = [0 for i in range(self.REGISTER_COUNT)]
        self.cache = Cache()

    # ----------------------------- #
    # -- Program Counter Options -- #
    # ----------------------------- #

    def get_pc(self) -> int:
        return self.pc

    def set_pc(self, pc: int):
        self.pc = pc

    def increment_pc(self):
        self.pc += 1

    def decrement_pc(self):
        self.pc -= 1

    # ----------------------------- #
    # -- Instruction Options     -- #
    # ----------------------------- #

    def get_instruction(self) -> Instruction:
        return self.instruction

    def set_instruction(self, instruction_bin: str):
        self.instruction.decode_instruction(instruction_bin)

    def get_register(self, index: int) -> int:
        return self.registers[index]

    def set_register(self, index: int, value: int):
        self.registers[index] = value

    # ----------------------------- #
    # -- CACHE Options           -- #
    # ----------------------------- #

    def get_cache(self) -> Cache:
        return self.cache
