from slither.core.variables.local_variable import LocalVariable as Slither_Local_Variable
from .local_variable import LocalVariable


class SolidityVariable(LocalVariable):
    def __init__(self, variable: Slither_Local_Variable):
        """
        Still missing
        original count, count of rep values
        """
        super().__init__(variable)

        # list of representative values for the parameter
        self._rep_values = []

