from slither.core.solidity_types.elementary_type import ElementaryType
from slither.core.solidity_types.array_type import ArrayType
from slither.core.solidity_types.mapping_type import MappingType


class Variable:
    def __init__(self, variable):
        # name of variable
        self._name = None

        """
        data type of variable, could be:
            elementary/primitive type
            array
            mapping
            user defined type
            
            function, rarely happen, a function can be assigned to a variable
            
        *****Instead of creating more fields or classes to store these information
             We will access the type information directly from the slither objects.
            
            size -> for elementary type, return size of type, e.g. uint256
            
            length -> for array type, length of array
            
            type_from -> mapping
            type_to -> mapping, could still be mapping, or array
            
        """
        self._type = None
        self._slither_variable = variable

    @property
    def name(self):
        return self._name

    @property
    def slither_variable(self):
        return self._slither_variable

    @property
    def type(self):
        return self._type

    @property
    def size(self):
        return self.type.size

    @property
    def length(self):
        return self.type.length

    @property
    def type_from(self):
        return self.type.type_from

    @property
    def type_to(self):
        return self.type.type_to

    def __str__(self):
        return self.__class__.__name__ + ": " + self.name + "=>" + str(self.type)

    def __repr__(self):
        return self.__class__.__name__ + ": " + self.name + "=>" + str(self.type)

    # end of region
    ###################################################################################
    ###################################################################################
    # region => public getters
    ###################################################################################
    ###################################################################################
