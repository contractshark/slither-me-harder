from slither.core.variables.local_variable import LocalVariable as Slither_Local_Variable

from .variable import Variable
from slither.core.solidity_types.user_defined_type import UserDefinedType
from slither.solc_parsing.declarations.contract import ContractSolc04
from slither.core.solidity_types.elementary_type import ElementaryType

class LocalVariable(Variable):
    def __init__(self, variable: Slither_Local_Variable):
        super().__init__(variable)
        self._name = variable.name
        if isinstance(variable.type, UserDefinedType):
            if isinstance(variable.type.type, ContractSolc04):
                self._type = ElementaryType('address')
            else:
                self._type = variable.type
        else:
            self._type = variable.type

