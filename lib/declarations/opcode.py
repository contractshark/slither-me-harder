class Opcode:
    def __init__(self):
        self.pc = None
        self.opcode = None
        self.size = None
        # if opcode is pushx
        self.value = None
        # original function object
        self.original_function = None
        # (offset, length)
        self.source_map = None
        self.source_code = None

        self.pre = None
        self.next = None
        self.block = None

    def set_original_function(self, original_function):
        self.original_function = original_function
        original_function.add_opcode(self)
        self.source_code = original_function.parent_contract.source_code_bytes[self.source_map[0]: self.source_map[0] + self.source_map[1]].decode('utf-8')

    def __str__(self):
        return f'{self.pc} {self.opcode}{" " + str(self.value) if self.value else ""}'

    def __repr__(self):
        return f'{self.pc} {self.opcode}{" " + str(self.value) if self.value else ""}'
