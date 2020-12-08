"""
    This module defines a instruction
    format for the hex input.
"""


class Instruction:

    __slots__ = [
        'format', 'opcode', 'reg1', 'reg2',
        'breg', 'dstreg', 'address'
    ]

    def __init__(self):
        self.format = None
        self.opcode = None
        self.reg1 = None
        self.reg2 = None
        self.breg = None
        self.dstreg = None
        self.address = None

    def __repr__(self):
        """     Troubleshooting     """
        return f'format {self.format} opcode {self.opcode} ' \
            'reg1 {self.reg1} reg2 {self.reg2} breg {self.breg} ' \
            'dstreg {self.dstreg} address {self.address}'

    def decode_instruction(self, instruction: str):
        instruction = instruction.replace('0x', '')
        instruction_bin = self.to_binary(instruction)
        self.format = self.to_hex(instruction_bin[0:2])
        self.opcode = self.to_hex(instruction_bin[2:8])

        # ----------------------------------- #
        # -- Arithmetic instruction format -- #
        # ----------------------------------- #

        if self.format == '0x0':
            self.reg1 = self.to_hex(instruction_bin[8:12])
            self.reg2 = self.to_hex(instruction_bin[12:16])
            self.breg = None
            self.dstreg = self.to_hex(instruction_bin[16:20])
            self.address = self.to_hex(instruction_bin[20:32])

        # --------------------------------------------- #
        # -- Conditional Branch and Immediate format -- #
        # --------------------------------------------- #

        elif self.format == '0x1':
            self.reg1 = None
            self.reg2 = None
            self.breg = self.to_hex(instruction_bin[8:12])
            self.dstreg = self.to_hex(instruction_bin[12:16])
            self.address = self.to_hex(instruction_bin[16:32])

        # ------------------------------- #
        # -- Unconditional Jump format -- #
        # ------------------------------- #

        elif self.format == '0x2':
            self.reg1 = None
            self.reg2 = None
            self.breg = None
            self.dstreg = None
            self.address = self.to_hex(instruction_bin[8:32])

        # ----------------------------------------- #
        # -- Input and Output instruction format -- #
        # ----------------------------------------- #

        elif self.format == '0x3':
            self.reg1 = self.to_hex(instruction_bin[8:12])
            self.reg2 = self.to_hex(instruction_bin[12:16])
            self.breg = None
            self.dstreg = None
            self.address = self.to_hex(instruction_bin[16:32])

        # ----------- #
        # -- ERROR -- #
        # ----------- #

        else:
            raise UnexpectedInstructionError(f'Unable to decode_instruction(instruction={instruction}).')

    @staticmethod
    def to_binary(instruction: str) -> str:
        instruction_bin = bin(int(instruction, 16))[2:]
        while len(instruction_bin) < 32:
            instruction_bin = "0" + instruction_bin
        return instruction_bin

    @staticmethod
    def to_hex(binary: str) -> str:
        return hex(int(binary, 2))


class UnexpectedInstructionError(Exception):
    pass
