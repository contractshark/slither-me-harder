from slither.core.expressions.binary_operation import BinaryOperation
from slither.core.expressions.identifier import Identifier
from slither.core.expressions.literal import Literal
from slither.core.expressions.tuple_expression import TupleExpression
from slither.core.expressions.unary_operation import UnaryOperation
from slither.core.solidity_types.array_type import ArrayType
from slither.core.solidity_types.elementary_type import ElementaryType
from slither.core.solidity_types.mapping_type import MappingType
from slither.core.solidity_types.user_defined_type import UserDefinedType
from slither.core.variables.state_variable import StateVariable as Slither_State_Variable
from slither.core.declarations.solidity_variables import SolidityVariableComposed as Slither_SolidityVariableComposed
from slither.core.declarations.solidity_variables import SolidityVariable as Slither_SolidityVariable

from .variable import Variable


class StateVariable(Variable):
    """
    State variable object.

    *** To be completed.
        ❌ Still need to add state variables that are not checked by require.
    """

    def __init__(self, variable: Slither_State_Variable):
        super().__init__(variable)
        # e.g."internal", "public" ,etc.
        self._visibility = None

        # whether this state variable is initialized by hard code during deployment.
        # both a = 0 and a = msg.sender are considered initialized
        # however, the later one also has _set_by_deployment being True
        self._initialized = None

        # if this state variable can be set using constructor.
        self._set_by_constructor = None

        # which variable was used to initialized the state variable
        # for example, now, msg.sender, etc.
        # type is string, should be enough for the moment.
        self._var_used_in_deployment = None

        # if this state variable is initialized at deployment using SolcVariable
        # a = now, a = msg.sender, etc.
        self._initialized_using_SolcVar = None

        # functions that read the current state variable.
        # specifically, read by requires.
        self._functions_read = set()

        # functions that writes to the current state variable.
        self._functions_written = set()

        # saw this somewhere in slither, may need more investigation to
        # find out about what it does exactly.
        """
        *** To be completed. 
            What is this about?
        """
        # self.f_write_conditions = []

        # modifiers that read the current state variable.
        self._modifiers_read = set()

        # modifiers that writes to the current state variable.
        # this doesn't often happen.
        # but when it does, it's not handdled....😒
        """
        *** To be completed.
            What to do when a modifier writes to a state variable? 
            How does it affect the dependency graph? 
        """
        self._modifiers_written = set()

        # requires that read the current state variable.
        # this attribute is not currently used, and may never be used...
        # I'm just gonna leave it here in case it is needed in the future...😒
        self._requires_read = set()

        # the default value of the state variable.
        # only available when state variable is not set by constructor.
        self._default_value = None

        self._setter(variable)

    ###################################################################################
    ###################################################################################
    # region => public getters
    ###################################################################################
    ###################################################################################

    @property
    def visibility(self):
        return self._visibility

    @property
    def initialized(self):
        return self._initialized

    @property
    def set_by_constructor(self):
        return self._set_by_constructor

    @property
    def set_by_deployment(self):
        return self._initialized_using_SolcVar

    @property
    def var_used_in_deployment(self):
        return self._var_used_in_deployment

    @property
    def functions_read(self):
        return list(self._functions_read)

    @property
    def functions_written(self):
        return list(self._functions_written)

    @property
    def modifiers_read(self):
        return list(self._modifiers_read)

    @property
    def modifiers_written(self):
        return list(self._modifiers_written)

    @property
    def requires_read(self):
        return list(self._requires_read)

    @property
    def default_value(self):
        return self._default_value

    def has_default_value(self):
        """
        Check if state variable has a default value.
        If a state variable needs be set by constructor, then it does not have a default value.

        Finished.
        """
        return not self._set_by_constructor

    def get_default_value(self):
        """
        Getting the default value of the state variable.
        Must call has_default_value() first.

        Finished.
        """
        if self._set_by_constructor:
            raise Exception(f'"{self.name}"" does not have a default value because it needs to be set by constructor. '
                            f'Please call "has_default_value()" prior to calling "get_default_value()"')
        else:
            return self._default_value


    # end of region
    ###################################################################################
    ###################################################################################
    # region => public getters
    ###################################################################################
    ###################################################################################

    ###################################################################################
    ###################################################################################
    # region => public setters
    ###################################################################################
    ###################################################################################

    def add_function_call(self, function_or_modifier, read_or_write, function_call):
        if function_or_modifier == "function":
            if read_or_write == "read":
                self._add_read_function(function_call)
            else:
                self._add_written_function(function_call)
        else:
            if read_or_write == "read":
                self._add_read_modifier(function_call)
            else:
                self._add_written_modifier(function_call)

    def add_read_require(self, require):
        self._requires_read.add(require)

    # end of region
    ###################################################################################
    ###################################################################################
    # region => public setters
    ###################################################################################
    ###################################################################################

    ###################################################################################
    ###################################################################################
    # region => private functions
    ###################################################################################
    ###################################################################################

    def _setter(self, variable: Slither_State_Variable):
        """
        Setting values when initializing

        Finished.
        """
        self._name = variable.name
        self._type = variable.type
        self._visibility = variable.visibility
        self._initialized = True if variable.initialized else False
        self._set_by_constructor = False
        self._initialized_using_SolcVar = False
        # self._default_value = \
        #     self._set_default_value(variable.type, variable.expression if variable.expression else None, self.name)

    def _add_read_function(self, function):
        """
        Adds a function that reads the state variable.
        """
        self._functions_read.add(function)

    def _add_written_function(self, function):
        """
        Adds a function that writes to the state variable.
        """
        # if the current function being added is the constructor,
        # we update the self.set_by_constructor to True
        if function.name == "constructor":
            self._set_by_constructor = True
        self._functions_written.add(function)

    def _add_read_modifier(self, modifier):
        """
        Adds a modifier that reads the state variable.
        """
        self._modifiers_read.add(modifier)

    def _add_written_modifier(self, modifier):
        """
        Adds a modifier that writes to the state variable.
        """
        self._modifiers_written.add(modifier)

    def _set_default_value(self, data_type, exp, name):
        """
        type:      data type of the state variable.
        exp:       expression of the static value assignment, such as  "msg.sender" for "owner = msg.sender".
        name:      state variable name.

        Sets the default value of the state variable.
        A default value only exists when the state variable is not modified by the constructor.

        *** To be completed.
            Handling more types. Such as 2 ** 64
        """

        deep_type = get_deepest_type(data_type)
        data_type_str = str(deep_type)

        if isinstance(exp, Literal):
            # if _exp is int, convert the number of python code.
            # using eval is for the cases of "1e10"
            if 'int' in str(exp.type):
                exp = eval(str(exp))
            # ❌ other types are still using string.
            else:
                exp = exp.value
        elif isinstance(exp, Identifier):
            """
                ❌ Only msg.sender or now etc. can be used for initial assignment. 
                However, for customized struct, it may work differently. 
                also a = 0, b = a
                if msg.sender, now is used, state variable can be set by constructor
                    more specifically, can be set at deployment. 

                *** To be completed
            """

            if isinstance(exp.value, Slither_SolidityVariableComposed) or \
                    isinstance(exp.value, Slither_SolidityVariable):
                self._initialized_using_SolcVar = True
                self._var_used_in_deployment = str(exp.value)

            exp = None
        elif isinstance(exp, BinaryOperation) or isinstance(exp, UnaryOperation) or isinstance(exp, TupleExpression):
            """
            ❌ So far, converting things like 
                2 ** 64 or -3, (2 + 3) / 4 
                To just python code, should mostly work. 
            """
            exp = eval(str(exp))
        elif not exp:
            """
                Makes the exp None. 
                ❌ There might be other cases. 
            """
            exp = eval(str(exp))
        else:
            raise Exception(f'Some unhandled cases happened. \n\t The exp "{str(exp)}"\'s '
                            f'type is "{type(exp)}"')

        default_value = self._default_value_helper(exp, deep_type, name)

        if data_type_str.startswith('int') or data_type_str.startswith('uint'):
            return int(default_value)
        elif data_type_str == 'bool':
            if default_value == 'true':
                return True
            else:
                return False
        elif data_type_str == 'string' or data_type_str == 'byte' or data_type_str == 'address':
            return default_value
        elif not default_value:
            return None
        else:
            raise Exception(f'Unhandled type: \n\t {data_type_str}')

    def _default_value_helper(self, value, data_type, name):
        """
        Helper for getting the default value of the state variable.
        If there is a default value statically assigned to the state variable, return default value.
        Otherwise, return the corresponding default solidity value for the data type.

        *** To be completed.
            Handling more types.
        """

        data_type_str = str(data_type)

        # There can also be <class 'slither.core.solidity_types.user_defined_type.UserDefinedType'>
        if isinstance(data_type, ElementaryType):
            if value:
                return value

            if data_type_str.startswith('int') or data_type_str.startswith('uint'):
                return '0'
            elif data_type_str == 'bool':
                return 'false'
            elif data_type_str == 'string':
                return ''
            elif data_type_str == 'byte':
                return '0x0'
            elif data_type_str == 'address':
                return '0x' + "".zfill(40)
            else:
                raise Exception(f'Unhandled Solidity Elementary Type. \n {data_type_str} for {name}')

        elif isinstance(data_type, UserDefinedType):
            print(f'Unhandled user defined type: \n\t{data_type_str} for {name}')
            return None
        else:
            raise Exception(f'Unhandled data type: \n\t{data_type_str} for {name}')
            return None

    # end of region
    ###################################################################################
    ###################################################################################
    # region => private functions
    ###################################################################################
    ###################################################################################


###################################################################################
###################################################################################
# region => utility functions
###################################################################################
###################################################################################

def get_deepest_type(data_type):
    if isinstance(data_type, MappingType):
        d_type = get_deepest_type(data_type.type_to)
    elif isinstance(data_type, ArrayType):
        d_type = get_deepest_type(data_type.type)
    elif isinstance(data_type, ElementaryType):
        d_type = data_type
    elif isinstance(data_type, UserDefinedType):
        d_type = data_type
        print(f'Unable to set default value for user defined data type: {str(data_type)}.')
    else:
        raise Exception(f'Unhandled type: \n\t {type(data_type)}')

    return d_type

# end of region
###################################################################################
###################################################################################
# region => utility functions
###################################################################################
###################################################################################
