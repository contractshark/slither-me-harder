from collections import defaultdict
import copy
import z3

from slither.core.solidity_types.type import Type
from typing import Dict, List, Any
from slither.solc_parsing.variables.state_variable import StateVariableSolc


def get_index_write_values(function, tc):
    # data_type => level => StateVariableSolc => value
    res: Dict[Type, Dict[int, Dict[StateVariableSolc, List[Any]]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for p_name, value in tc.items():
        param = function.get_parameter_by_name(p_name)
        if not param: continue
        for (level, SVs) in param.state_var_index_write.items():
            for sv in SVs:
                if value not in res[param.type][level][sv]:
                    res[param.type][level][sv].append(value)
    return res


def make_copy(index_values):
    res = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for data_type, levels in index_values.items():
        for level, SVs in levels.items():
            for sv, values in SVs.items():
                for value in values:
                    if value not in res[data_type][level][sv]:
                        res[data_type][level][sv].append(value)
    return res


class Transaction:
    def __init__(self, function, tc, parent_transaction, new_coverage, status, contract):
        self._function = function
        self._tc = tc
        self._parent = parent_transaction
        self._children = []
        self._index_values = get_index_write_values(function, tc)   # data_type => level => StateVariableSolc => value
        self._all_index_values = self._get_previous_index_values()
        self._new_coverage = new_coverage
        self._status = status
        new_coverage_weight = 10 if new_coverage else 0
        self._weight = new_coverage_weight + status if status else 0
        self._depth = 0 if not parent_transaction else parent_transaction.depth + 1

        self._can_enter_functions = None
        self.set_can_enter_functions(contract)
        if parent_transaction:
            parent_transaction.add_child(self)

    def __str__(self):
        return f'{self.function if self.function else "constructor()"}  {self.tc}'

    def __repr__(self):
        return f'{self.function if self.function else "constructor()"}  {self.tc}'

    @property
    def depth(self):
        return self._depth

    @property
    def can_enter_functions(self):
        return self._can_enter_functions

    def set_can_enter_functions(self, contract):
        res = []
        if self.function and self.function.is_suicidal:
            self._can_enter_functions = res
            return

        candidate_functions = contract.fuzzing_candidate_functions
        for function in candidate_functions:

            s = function.z3.solver
            s.push()
            function.z3.load_z3_state_values()
            if s.check() == z3.sat:
                res.append(function)
            s.pop()
        self._can_enter_functions = res

    def add_child(self, transaction):
        self._children.append(transaction)

    def _get_previous_index_values(self):
        res = make_copy(self.this_index_values_dic)
        temp = self.parent
        while temp:
            for data_type, levels in temp.previous_index_values_dic.items():
                for level, SVs in levels.items():
                    for sv, values in SVs.items():
                        for value in values:
                            if value not in res[data_type][level][sv]:
                                res[data_type][level][sv].append(value)
            temp = temp.parent
        return res

    @property
    def new_coverage(self):
        return self._new_coverage

    @property
    def status(self):
        return self._status

    @property
    def weight(self):
        return self._weight

    @property
    def this_index_values_dic(self):
        return self._index_values

    @property
    def previous_index_values_dic(self):
        return self._all_index_values

    @property
    def parent(self):
        return self._parent

    @property
    def children(self):
        return self.children

    @property
    def function(self):
        return self._function

    @property
    def tc(self):
        return self._tc
