from os_ import alu
from os_.mmu import MMU
from os_.pcb import PCB
from os_.cpu_state import CPUState
from os_.cache import Cache
from os_.logical_address import LogicalAddress
from os_.config import ENDED_STATE
from os_.synchronization import synchronized
from os_.sync_print import sync_print

CPU_DEBUG = False


class CPU:

    def __init__(self, id_: int, mmu: MMU):
        self.cpu_id = id_
        self.mmu = mmu
        self.cpu_state = CPUState()
        self.cache = Cache()
        self.logical_address = LogicalAddress()
        self._is_running_process = False
        self.is_running = True
        self.is_spinning = False
        self.is_process_started = False
        self.is_process_complete = False
        self.cpu_is_interrupted = False
        self.current_pcb = None

        # -- DEBUGGING -- #
        self.jobs_completed = 0

    @synchronized
    def end_cpu(self):
        self.is_running = False

    def run(self):
        while self.is_running is True:
            if self.is_process_running() is True:
                self.initialize_cpu()
                self.run_process()
                self.set_process_running(False)

    @synchronized
    def run_pcb(self, pcb: PCB):
        while self.is_spinning is True:
            pass
        self.current_pcb = pcb
        self.set_process_running(True)

    def initialize_cpu(self):
        # -- Set CPU State -- #
        self.cpu_state = self.current_pcb.get_cpu_state()
        # -- Set Cache from CPU State -- #
        self.cache = self.cpu_state.get_cache()
        # -- Copy Program Counter -- #
        self.cpu_state.set_pc(self.cpu_state.get_pc())
        # -- Copy Registers -- #
        for i in range(CPUState.REGISTER_COUNT):
            self.cpu_state.set_register(index=i, value=self.cpu_state.get_register(index=i))

    def is_process_running(self) -> bool:
        return self._is_running_process

    @synchronized
    def set_process_running(self, b: bool):
        self._is_running_process = b

    def run_process(self):
        self.is_spinning = True
        while self.is_spinning is True:
            pc = self.cpu_state.get_pc()
            instruction_str = self.fetch(address=self.cpu_state.get_pc())

            self.cpu_state.increment_pc()
            if self.cpu_is_interrupted is False:
                self.decode(instruction_str)
                instruction = self.cpu_state.get_instruction()
                sync_print(
                    f'DEBUG: [CPU_ID {self.cpu_id} PID {self.current_pcb.job_id} pc {pc}]'
                    f' Fetch {instruction_str} -> {instruction}'
                ) if CPU_DEBUG is True else None

                if instruction.format == '0x0':
                    self.execute_arithmetic(
                        opcode_hex=instruction.opcode,
                        s1_hex=instruction.reg1,
                        s2_hex=instruction.reg2,
                        dr_hex=instruction.address,
                    )
                elif instruction.format == '0x1':
                    self.execute_conditional_branch(
                        opcode_hex=instruction.opcode,
                        br_hex=instruction.breg,
                        dr_hex=instruction.dstreg,
                        address_hex=instruction.address,
                    )
                elif instruction.format == '0x2':
                    self.execute_unconditional_jump(
                        opcode_hex=instruction.opcode,
                        address_hex=instruction.address,
                    )
                elif instruction.format == '0x3':
                    self.execute_io(
                        opcode_hex=instruction.opcode,
                        r1_hex=instruction.reg1,
                        r2_hex=instruction.reg2,
                        address_hex=instruction.address
                    )
                else:
                    raise UnexpectedCPUError(
                        f'run_process(...) unable to match instruction->format {instruction.format}.'
                    )

            if self.cpu_is_interrupted is True:
                self.cpu_state.decrement_pc()
                self.cpu_is_interrupted = False

    def fetch(self, address: int) -> str:
        self.logical_address.convert_from_raw_address(address)
        self.handle_interrupt(self.logical_address)
        return self.mmu.read_cache(logical_address=self.logical_address, cache=self.cache)

    def decode(self, instruction: str):
        if self.cpu_is_interrupted is True:
            return
        self.cpu_state.set_instruction(instruction)

    def handle_interrupt(self, logical_address: LogicalAddress):
        if self.mmu.check_for_interrupt(logical_address, self.cache, self.current_pcb) is True:
            self.is_spinning = False
            self.cpu_is_interrupted = True

    def execute_io(self, opcode_hex: str, r1_hex: str, r2_hex: str, address_hex: str):
        # -- Convert HEX to INT -- #
        r1_int = int(r1_hex, 0)
        r2_int = int(r2_hex, 0)
        address_int = int(address_hex, 0)

        # -- Check for Interrupts -- #
        if self.cpu_is_interrupted is True:
            return

        # Reads content of I/P buffer into an accumulator or a register #
        if opcode_hex == '0x0':
            if address_int == 0:
                word_address = self.cpu_state.get_register(index=r2_int) // 4
            else:
                word_address = address_int // 4
            self.logical_address.convert_from_raw_address(word_address)

            # -- Check for Interrupts -- #
            self.handle_interrupt(self.logical_address)
            if self.cpu_is_interrupted is True:
                return

            self.cpu_state.set_register(
                index=r1_int,
                value=int(
                    self.mmu.read_cache(self.logical_address, self.cache),
                    0),  # HEX TO INT
            )

        # Writes the content of accumulator into Output buffer #
        elif opcode_hex == '0x1':
            word_address = address_int // 4 if r1_hex == r2_hex else int(self.cpu_state.get_register(index=r2_int)) // 4
            self.logical_address.convert_from_raw_address(word_address)

            # -- Check for Interrupts -- #
            self.handle_interrupt(self.logical_address)
            if self.cpu_is_interrupted is True:
                return

            self.mmu.write_cache(
                logical_address=self.logical_address,
                data=int_to_hex_size_8(self.cpu_state.get_register(r1_int)),
                cache=self.cache
            )

        # Custom Error #
        else:
            raise UnexpectedCPUError(f'execute_io(...) unable to match opcode {opcode_hex}.')

    def execute_unconditional_jump(self, opcode_hex: str, address_hex: str):
        # -- Convert HEX to INT -- #
        address_int = int(address_hex, 0)

        # -- Check for Interrupts -- #
        if self.cpu_is_interrupted is True:
            return

        # ------------------------ #
        # -- Opcode Definitions -- #
        # ------------------------ #

        # Logical end of program #
        if opcode_hex == '0x12':
            self.jobs_completed += 1
            self.is_spinning = False
            self.mmu.write_to_ram(self.current_pcb)
            self.current_pcb.set_state(ENDED_STATE)

        # Jumps to a specified location #
        elif opcode_hex == '0x14':
            self.cpu_state.set_pc(pc=address_int)

        # Custom Error #
        else:
            raise UnexpectedCPUError(f'execute_unconditional_jump(...) unable to match opcode {opcode_hex}.')

    def execute_conditional_branch(self, opcode_hex: str, br_hex: str, dr_hex: str, address_hex: str):
        # -- Convert HEX to INT -- #
        br_int = int(br_hex, 0)
        dr_int = int(dr_hex, 0)
        address_int = int(address_hex, 0)

        # -- Check for Interrupts -- #
        if self.cpu_is_interrupted is True:
            return

        # ------------------------ #
        # -- Opcode Definitions -- #
        # ------------------------ #

        # Stores content of a reg. into an address #
        if opcode_hex == '0x2':
            word_address = self.cpu_state.get_register(index=dr_int) // 4
            self.logical_address.convert_from_raw_address(address=word_address)

            # -- Check for Interrupts -- #
            self.handle_interrupt(self.logical_address)
            if self.cpu_is_interrupted is True:
                return

            self.mmu.write_cache(
                logical_address=self.logical_address,
                data=int_to_hex_size_8(self.cpu_state.get_register(index=br_int)),
                cache=self.cache
            )
        # Loads the content of an address into a reg #
        elif opcode_hex == '0x3':
            word_address = self.cpu_state.get_register(index=br_int) // 4
            self.logical_address.convert_from_raw_address(address=word_address)

            # -- Check for Interrupts -- #
            self.handle_interrupt(self.logical_address)
            if self.cpu_is_interrupted is True:
                return

            self.mmu.read_cache(
                logical_address=self.logical_address,
                cache=self.cache
            )
        # Transfers address/data directly into a register #
        elif opcode_hex == '0xb':
            self.cpu_state.set_register(index=dr_int, value=address_int)

        # Adds a data value directly to the content of a register #
        elif opcode_hex == '0xc':
            acc = alu.add(
                r1=self.cpu_state.get_register(index=dr_int),
                r2=address_int
            )
            self.cpu_state.set_register(index=dr_int, value=acc)

        # Multiplies a data value directly with the content of a register #
        elif opcode_hex == '0xd':
            acc = alu.multi(
                r1=self.cpu_state.get_register(index=dr_int),
                r2=address_int
            )
            self.cpu_state.set_register(index=dr_int, value=acc)

        # Divides a data directly into the content of a register #
        elif opcode_hex == '0xe':
            acc = alu.div(
                r1=self.cpu_state.get_register(index=dr_int),
                r2=address_int
            )
            self.cpu_state.set_register(index=dr_int, value=acc)

        # Loads a data/address directly to the content of a register #
        elif opcode_hex == '0xf':
            self.cpu_state.set_register(index=dr_int, value=address_int)

        # Sets the D-reg to 1 if first S-reg is less than a data; 0 otherwise #
        elif opcode_hex == '0x11':
            if alu.less_than(
                    r1=self.cpu_state.get_register(index=br_int),
                    r2=address_int
            ):
                self.cpu_state.set_register(index=dr_int, value=1)
            else:
                self.cpu_state.set_register(index=dr_int, value=0)

        # Branches to an address when content of B-reg = D-reg #
        elif opcode_hex == '0x15':
            if alu.is_branch_equal_to(
                    breg=self.cpu_state.get_register(index=br_int),
                    dreg=self.cpu_state.get_register(index=dr_int)
            ):
                self.cpu_state.set_pc(pc=address_int//4)

        # Branches to an address when content of B-reg <> D-reg #
        elif opcode_hex == '0x16':
            if alu.is_branch_not_equal_to(
                    breg=self.cpu_state.get_register(index=br_int),
                    dreg=self.cpu_state.get_register(index=dr_int)
            ):
                self.cpu_state.set_pc(pc=address_int//4)

        # Branches to an address when content of B-reg = 0 #
        elif opcode_hex == '0x17':
            if alu.is_branch_zero(
                    breg=self.cpu_state.get_register(index=br_int),
            ):
                self.cpu_state.set_pc(pc=address_int//4)

        # Branches to an address when content of B-reg <> 0 #
        elif opcode_hex == '0x18':
            if alu.is_branch_not_zero(
                    breg=self.cpu_state.get_register(index=br_int),
            ):
                self.cpu_state.set_pc(pc=address_int//4)

        # Branches to an address when content of B-reg > 0 #
        elif opcode_hex == '0x19':
            if alu.is_branch_positive(
                    breg=self.cpu_state.get_register(index=br_int),
            ):
                self.cpu_state.set_pc(pc=address_int//4)

        # Branches to an address when content of B-reg < 0 #
        elif opcode_hex == '0x1a':
            if alu.is_branch_negative(
                    breg=self.cpu_state.get_register(index=br_int),
            ):
                self.cpu_state.set_pc(pc=address_int//4)

        # Custom Error #
        else:
            raise UnexpectedCPUError(f'execute_conditional_branch(...) unable to match opcode {opcode_hex}.')

    def execute_arithmetic(self, opcode_hex: str, s1_hex: str, s2_hex: str, dr_hex: str):
        # -- Convert HEX to INT -- #
        s1_int = int(s1_hex, 0)
        s2_int = int(s2_hex, 0)
        dr_int = int(dr_hex, 0)

        # -- Check for Interrupts -- #
        if self.cpu_is_interrupted is True:
            return

        # ------------------------ #
        # -- Opcode Definitions -- #
        # ------------------------ #

        # Transfers the content of one register into another #
        if opcode_hex == '0x4':
            self.cpu_state.set_register(
                index=s1_int,
                value=self.cpu_state.get_register(s2_int)
            )

        # Adds content of two S-regs into D-reg #
        elif opcode_hex == '0x5':
            acc = alu.add(
                r1=self.cpu_state.get_register(s1_int),
                r2=self.cpu_state.get_register(s2_int)
            )
            self.cpu_state.set_register(dr_int, acc)

        # Subtracts content of two S-regs into D-reg #
        elif opcode_hex == '0x6':
            acc = alu.sub(
                r1=self.cpu_state.get_register(s1_int),
                r2=self.cpu_state.get_register(s2_int)
            )
            self.cpu_state.set_register(dr_int, acc)

        # Multiplies content of two S-regs into D-reg #
        elif opcode_hex == '0x7':
            acc = alu.multi(
                r1=self.cpu_state.get_register(s1_int),
                r2=self.cpu_state.get_register(s2_int)
            )
            self.cpu_state.set_register(dr_int, acc)

        # Divides content of two S-regs into D-reg #
        elif opcode_hex == '0x8':
            acc = alu.div(
                r1=self.cpu_state.get_register(s1_int),
                r2=self.cpu_state.get_register(s2_int)
            )
            self.cpu_state.set_register(dr_int, acc)

        # Logical AND of two S-regs into D-reg #
        elif opcode_hex == '0x9':
            acc = alu.and_operator(
                r1=self.cpu_state.get_register(s1_int),
                r2=self.cpu_state.get_register(s2_int)
            )
            self.cpu_state.set_register(dr_int, acc)

        # Logical OR of two S-regs into D-reg #
        elif opcode_hex == '0xa':
            acc = alu.or_operator(
                r1=self.cpu_state.get_register(s1_int),
                r2=self.cpu_state.get_register(s2_int)
            )
            self.cpu_state.set_register(dr_int, acc)

        # Sets the D-reg to 1 if first S-reg is less than the B-reg; 0 otherwise #
        elif opcode_hex == '0x10':
            if alu.less_than(
                    r1=self.cpu_state.get_register(s1_int),
                    r2=self.cpu_state.get_register(s2_int)
            ):
                self.cpu_state.set_register(dr_int, 1)
            else:
                self.cpu_state.set_register(dr_int, 0)

        # Custom Error #
        else:
            raise UnexpectedCPUError(f'execute_arithmetic(...) unable to match opcode {opcode_hex}.')


class UnexpectedCPUError(Exception):
    pass


def int_to_hex_size_8(x: int) -> str:
    """
    Takes and int() and converts to a HEX, prepending
    0's where needed to reach size of 8 digits.
    """
    x_hex = hex(x).replace('0x', '')
    while len(x_hex) < 8:
        x_hex = "0" + x_hex
    x_hex = '0x' + x_hex
    return x_hex
