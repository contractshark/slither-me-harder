from slither.core.declarations import SolidityFunction as Slither_SolidityFunction

from slither.solc_parsing.declarations.modifier import ModifierSolc as Slither_ModifierSolc
from slither.solc_parsing.declarations.function import FunctionSolc as Slither_FunctionSolc

from slither.core.declarations.function import Function as Slither_Function
from slither.core.declarations.modifier import Modifier as Slither_Modifier
from slither.core.declarations.solidity_variables import SolidityVariableComposed as Slither_SolidityVariableComposed
from slither.core.declarations.solidity_variables import SolidityVariable as Slither_SolidityVariable

from slither.slithir.operations import SolidityCall as Slither_SolidityCall
from slither.solc_parsing.cfg.node import NodeSolc as Slither_NodeSolc
from slither.solc_parsing.variables.local_variable import LocalVariableSolc

from .local_variable import LocalVariable
from .require import Require
from .state_variable import StateVariable
from .parameter import Parameter
from .solidity_variable import SolidityVariable
from .solidity_variable_composed import SolidityVariableComposed

from slither.slithir.operations.member import Member
from slither.slithir.operations.type_conversion import TypeConversion
from slither.slithir.variables.constant import Constant
from slither.slithir.operations.binary import Binary

from typing import Set, Dict
from slither.slithir.operations import Index
from slither.core.variables.variable import Variable
from slither.analyses.data_dependency.data_dependency import is_dependent
from slither.solc_parsing.variables.state_variable import StateVariableSolc
from slither.slithir.variables.reference import ReferenceVariable
from slither.slithir.operations.assignment import Assignment
from web3 import Web3
from slither.core.solidity_types.user_defined_type import UserDefinedType
from collections import defaultdict

require_functions = [Slither_SolidityFunction("require(bool)"),
                     Slither_SolidityFunction("require(bool,string)")]


def parse_constant(value, slither_type):
    if slither_type.name == 'address':
        if isinstance(value, str):
            return value
        else:
            return '0x' + hex(value)[2:].zfill(40)
    elif slither_type.name == 'string' or 'byte' in slither_type.name:
        if isinstance(value, int):
            return value
        else:
            return Web3.toInt(value.encode('utf-8'))
    else:
        return value


class FunctionCall:
    def __init__(self):

        # e.g. "constructor".
        self._name = None

        # e.g. "constructor(uint256,uint256)"
        self._full_name = None

        # e.g  "HoloToken.constructor(uint256,uint256)"
        self._canonical_name = None

        # e.g. "constructor(bytes32[]) returns()".
        self._signature = None

        self._solidity_signature = None

        # contract object where current function belongs.
        self._parent_contract = None

        # set of requires.
        self._requires = set()

        # dic of parameters with name as key.
        self._parameters = {}

        # with parameter name as key, parameter object as val
        self._parameters_used_as_index = {}

        # source code of function, currently not available
        self._source_code = None

        # set of state variables written by the function.
        self._state_variables_written = set()

        # set of state variables read by the function.
        # specifically, read by the requires within the function.
        self._state_variables_read = set()

        # a dic for keeping all the necessary local variables
        self._local_variables = {}

        # local variables read by the function.
        # specifically, read by the requires within the function.
        self._local_variables_read = set()

        # local variables written by the function.
        self._local_variables_written = set()

        # declared by which contract, functions can be inherited from parent contract.
        # especially constructor
        self._declared_by = None

        self._slither_function = None

        self._constants = defaultdict(set)


    ###################################################################################
    ###################################################################################
    # region => public getters
    ###################################################################################
    ###################################################################################


    @property
    def name(self):
        return self._name

    @property
    def full_name(self):
        return self._full_name

    @property
    def canonical_name(self):
        return self._canonical_name

    @property
    def signature(self):
        return self._signature

    @property
    def solidity_signature(self):
        return self._solidity_signature

    @property
    def parent_contract(self):
        return self._parent_contract

    @property
    def requires(self):
        return list(self._requires)

    @property
    def total_requires(self):
        return len(self._requires)

    @property
    def parameters(self):
        return list(self._parameters.values())

    @property
    def parameters_dic(self):
        return self._parameters

    def get_parameter_by_name(self, name):
        return self._parameters.get(name)

    def add_parameter(self, parameter):
        ignored = ['now', 'this', 'abi', 'msg', 'tx', 'block', 'super',
                   'block.coinbase', 'block.difficulty', 'block.gaslimit',
                   'block.number', 'block.timestamp', 'block.blockhash',
                   'msg.data', 'msg.gas', 'msg.sig', 'tx.gasprice', 'tx.origin']

        # Basically, we only keep msg.sender and msg.value as parameters

        if parameter.name not in ignored:
            self._parameters[parameter.name] = parameter

    # @property
    # def parameter_names(self):
    #     return ', '.join([p.name for p in self._parameters])

    @property
    def parameters_used_as_index(self):
        return list(self._parameters_used_as_index.values())

    @property
    def parameters_used_as_index_dic(self):
        return self._parameters_used_as_index

    @property
    def source_code(self):
        return self._source_code

    @property
    def state_variables_written(self):
        return list(self._state_variables_written)

    @property
    def state_variables_read(self):
        return list(self._state_variables_read)

    @property
    def local_variables(self):
        return list(self._local_variables.values())

    @property
    def local_variables_dic(self):
        return self._local_variables

    def add_local_variable(self, local_variable):
        self._local_variables[local_variable.name] = local_variable

    @property
    def local_variables_read(self):
        return list(self._local_variables_read)

    @property
    def local_variables_written(self):
        return list(self._local_variables_written)

    @property
    def declared_by(self):
        return self._declared_by

    @property
    def slither_function(self):
        return self._slither_function

    @property
    def constants_dic(self):
        return self._constants

    # end of region
    ###################################################################################
    ###################################################################################
    # region => public getters
    ###################################################################################
    ###################################################################################

    ###################################################################################
    ###################################################################################
    # region => private functions
    ###################################################################################
    ###################################################################################

    def _function_call_setter(self, function, parent_contract):
        """
        Setting values when initializing

        Finished.
        """
        self._name = function.name
        self._full_name = function.full_name
        self._canonical_name = function.canonical_name
        self._signature = function.signature_str
        self._solidity_signature = function.solidity_signature
        self._parent_contract = parent_contract
        self._declared_by = function.contract_declarer.name
        self._slither_function = function

        self._load_parameters(function)
        self._load_variables(function)
        self._load_requires(function)

        self.analyze_para_index_usage()

        self.find_used_constants()
        # if self.parent_contract.name == 'MultiSigRoot':
        #     print(f'{self.parent_contract} {self.canonical_name} => {self.parameters_used_as_index}')

    def _load_parameters(self, function_call):
        """
        Creating the parameter objects.

        Finished.
        """
        for variable in function_call.parameters:
            new_parameter = Parameter(variable)
            self.add_parameter(new_parameter)
            self.add_local_variable(new_parameter)

    def _load_variables(self, function_call):
        """
        Loading both local and state variable objects.

        Finished.
        """
        # cannot load the read state variables outside of requires, this will mess up the dependency
        # self._load_state_variables(function_call.state_variables_read, 'read')
        self._load_state_variables(function_call.state_variables_written, 'written')
        # it should be fine to load the local variables read.
        self._load_local_variables(function_call.variables_read, 'read')
        self._load_local_variables(function_call.variables_written, 'written')

    def _load_state_variables(self, variables, read_or_write):
        """
        Loading state variable objects.

        Finished.
        """
        for variable in variables:
            # get from dict if already exist
            if variable.name in self._parent_contract.state_variables_dic:
                new_variable = self._parent_contract.state_variables_dic[variable.name]
            else:
                new_variable = StateVariable(variable)
                self._parent_contract.state_variables_dic[variable.name] = new_variable

            # adding the current function/modifier into the state variable.
            new_variable.add_function_call(self.__class__.__name__.lower(), read_or_write, self)

            # adding the new state variable to the current function
            getattr(self, '_state_variables_' + read_or_write).add(new_variable)

    def _load_local_variables(self, variables, read_or_write):
        """
        Loading local variable object.

        Finished.
        """
        for variable in variables:
            # Slither_SolidityVariableComposed is msg.send etc.
            # There can be other types such as
            #       slither.solc_parsing.variables.local_variable_init_from_tuple.LocalVariableInitFromTupleSolc
            #           https://github.com/crytic/slither/blob/3e1f0d0a2fe8a8beb01121a6d3fc35b7bf033283/slither/core/variables/local_variable_init_from_tuple.py#L3
            #           It rarely happens
            #       slither.core.declarations.solidity_variables.SolidityVariable (such as evm time, "now")
            #           https://github.com/crytic/slither/blob/master/slither/core/declarations/solidity_variables.py
            self.load_local_variables_helper(variable, read_or_write)

    def load_local_variables_helper(self, variable, read_or_write):
        # StateVariableSolc was in the following list, but has been removed
        # Because we are only loading local variable
        # At this moment, msg.sender, etc. are considered as local variables.

        if type(variable) not in [LocalVariableSolc, Slither_SolidityVariableComposed, Slither_SolidityVariable]:
            return

        # There was a check of whether "variable" is None in the if condition
        # Because the returns list can sometimes have None objects in there.
        # this is currently handle by checking the variable type above.

        if variable.name in self._local_variables:
            new_variable = self._local_variables[variable.name]
        else:
            new_variable = None
            if isinstance(variable, LocalVariableSolc):
                new_variable = LocalVariable(variable)
            elif isinstance(variable, Slither_SolidityVariableComposed):
                # print(variable)
                if variable.name == 'msg.value' and (self.slither_function.payable or self.slither_function.is_constructor):
                    new_variable = SolidityVariableComposed(variable)
                    self.add_parameter(new_variable)
                elif variable.name != 'msg.value':
                    new_variable = SolidityVariableComposed(variable)
                    self.add_parameter(new_variable)
            elif isinstance(variable, Slither_SolidityVariable):
                new_variable = SolidityVariable(variable)
                self.add_parameter(new_variable)
            else:
                raise Exception(f'Variable "{variable.name}" type "{type(variable)}" unhandled.')
            if new_variable:
                self.add_local_variable(new_variable)

        # duplicate has been checked.
        getattr(self, '_local_variables_' + read_or_write).add(new_variable)

    def _load_requires(self, function_call):
        """
        Loading front require objects in a function.

        Notes:
            ✔What about requires from calls to another function?
                ✔*** This is currently not considered since they are not the pre-conditional requires of the parent
                    function.

            ❌We need to differentiate requires that are not pre-conditions.
                Either requires that does not appear at the beginning of the function call, or post condition modifiers.
                This maybe achieved by using IR.
                    ✔*** requires doesn't appear at the beginning of the function call as been removed.
                    ❌*** post-conditional requires from modifiers due to _; still needs to be removed.

            ✔However, some requires might not appear at the beginning, yet they are still checking the pre-condition.
            ❌This is also indirect read of variables, which has not been handled.
                e.g.
                    sender = msg.sender;
                    require(owner == sender);
        """
        if type(function_call) in [Slither_Function, Slither_FunctionSolc]:
            for node in function_call.nodes:
                # https://github.com/crytic/slither/blob/master/slither/core/cfg/node.py
                # node_type => 0 represents Entry Point Node, we can safely skip this.
                # node_type => 19 (0x13 in hex) represents Variable Declaration, we can safely skip this because
                # requires appears after new variable declaration should still be pre-condition checking.
                if node.type in [0, 19]:
                    continue

                # require() is a internal call, this finds potential require statement.
                if node.internal_calls:
                    # check if the call is actually require call.
                    """
                    Multiple internal calls can happen within one node. 
                    Such as require(check())
                    Currently, this is still treated as normal precondition require. 
                    As long as there is a require call, this node is considered as a require. 
                    """
                    found_require = False
                    for internal_call in node.internal_calls:
                        if internal_call in require_functions:
                            found_require = self._create_require(node)
                            break

                    # if no require found after internal call.
                    # Later requires are deemed to be post condition checking
                    # And will be ignored.
                    if found_require:
                        continue
                    else:
                        break
                else:
                    # if not. Requires appear after this are not pre-conditional checking requires.
                    break
        elif type(function_call) in [Slither_Modifier, Slither_ModifierSolc]:
            """
            All requires from modifiers are been loaded regardless pre or post condition check. 
            """
            for ir in function_call.slithir_operations:
                if isinstance(ir, Slither_SolidityCall) and ir.function in require_functions:
                    self._create_require(ir.node)
        else:
            raise Exception(f'Unhandled function call type {type(function_call)}.')

    def _create_require(self, require: Slither_NodeSolc):
        """
        Creating require objects.

        *** To be completed.
            ❌There could be duplicate state or local variables added to the function.
                ✔There shouldn't be any duplicate state variables since they are only created once, and they are added to a set.
                There might be duplicate local variables.
            Because all state and local variables from modifier objects have already been loaded using load_modifiers().
            Take a look into this and confirm.
        """
        try:
            new_require = Require(require, self)
        except:
            return False

        # adding state variables read from the require to current function_call.
        for state_variable in new_require.state_variables_read:
            self._state_variables_read.add(state_variable)

        # adding local variables read from the require to current function_call.
        for local_variable in new_require.local_variables_read:
            self._local_variables_read.add(local_variable)

        self._requires.add(new_require)
        return True

    def analyze_para_index_usage(self):
        params_index_read = self.find_index_read()
        params_index_write = self.find_index_write()

        for (param, level_SVs) in params_index_read.items():
            if self.get_parameter_by_name(param.name):
                self.get_parameter_by_name(param.name).set_state_var_level_index_read(level_SVs)

        for (param, level_SVs) in params_index_write.items():
            if self.get_parameter_by_name(param.name):
                self.get_parameter_by_name(param.name).set_state_var_level_index_write(level_SVs)

    def find_index_read(self):
        result: Dict[Variable, Dict[int, Set[StateVariableSolc]]] = defaultdict(lambda: defaultdict(set))

        for ir in self.slither_function.all_slithir_operations():
            if isinstance(ir, Index):
                self.inspect_index_ir(ir, result)
        return result

    def find_index_write(self):
        result: Dict[Variable, Dict[int, Set[StateVariableSolc]]] = defaultdict(lambda: defaultdict(set))

        for assignment_ir in self.slither_function.all_slithir_operations():
            if (isinstance(assignment_ir, Assignment) and isinstance(assignment_ir.lvalue, ReferenceVariable) and
                    isinstance(assignment_ir.lvalue.points_to_origin, StateVariableSolc)):
                self.find_ref_val_index_usage(assignment_ir.lvalue, assignment_ir.node, result)
        return result

    def find_ref_val_index_usage(self, ref_var, node, index_usage: Dict[Variable, Dict[int, Set[StateVariableSolc]]]):
        # instead of looking only into the node's irs, we can look in the whole function, and discover indirect index
        # access write.
        # this can be improved
        for ir in node.irs:
            if isinstance(ir, Index) and ref_var == ir.lvalue:
                self.inspect_index_ir(ir, index_usage)
                for ir_v in ir.variables:
                    if isinstance(ir_v, ReferenceVariable):
                        self.find_ref_val_index_usage(ir_v, node, index_usage)

    def inspect_index_ir(self, ir, index_usage: Dict[Variable, Dict[int, Set[StateVariableSolc]]]):
        params = self.slither_function.parameters + self.slither_function.solidity_variables_read
        for param in params:
            if is_dependent(ir.variable_right, param, self.parent_contract.slither_contract):
                level = 0
                temp = ir.variable_left
                while isinstance(temp, ReferenceVariable):
                    temp = temp.points_to
                    level += 1
                if isinstance(temp, StateVariableSolc):
                    index_usage[param][level].add(temp)

    def find_used_constants(self):
        IF = 0x12
        IFLOOP = 0x15

        for ir in self.slither_function.all_slithir_operations():
            if isinstance(ir, Slither_SolidityCall) and ir.function in require_functions:
                for require_ir in ir.node.irs:
                    # Irs that are in require statements, not the require call ir
                    if ir != require_ir:
                        self.find_constants(require_ir)

            node_type = ir.node.type
            if node_type == IF or node_type == IFLOOP:
                self.find_constants(ir)

    def find_constants(self, ir):
        if isinstance(ir, Member):
            return

        for r in ir.read:
            if isinstance(r, Constant):
                if isinstance(r.type, UserDefinedType):
                    continue
                elif isinstance(ir, Slither_SolidityCall) and r.type.name == 'string':
                    continue
                if isinstance(ir, TypeConversion) and len(ir.read) == 1:
                    if isinstance(ir.type, UserDefinedType):
                        continue
                    else:
                        self._constants[ir.type].add(parse_constant(r.value, ir.type))
                else:
                    self._constants[r.type].add(parse_constant(r.value, r.type))
                    # if isinstance(ir, Binary):
                    #     constant_value
                    #     self._constants[r.type].add(r.value)
                    #
                    #     if ir.type_str in ['<', '>']:
                    #         self._constants[r.type].add(r.value + 1)
                    #         self._constants[r.type].add(r.value - 1)




    # end of region
    ###################################################################################
    ###################################################################################
    # region => private functions
    ###################################################################################
    ###################################################################################

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
