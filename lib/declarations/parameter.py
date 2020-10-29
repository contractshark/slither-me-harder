from slither.core.variables.local_variable import LocalVariable as Slither_Local_Variable
from .local_variable import LocalVariable
from slither.core.solidity_types.elementary_type import ElementaryType


class Parameter(LocalVariable):
    def __init__(self, variable: Slither_Local_Variable):
        """
        Still missing
        original count, count of rep values
        """
        super().__init__(variable)

        # list of representative values for the parameter
        self._base_rep_values = []
        self._used_as_index = False

        self._state_var_index_read = dict()  # Dict[int, Set[StateVariableSolc]]
        self._state_var_index_write = dict()
        self._used_with_constant = False

        self._additional_rep_values_by_state = {}

        # this is a really bad way of doing it.
        # since combining base and additional rep values may produce elements in different order
        # it is currently handled by creating a temp one.
        # Something will likely go wrong in the future when code is modified.

    @property
    def base_rep_values(self):
        return self._base_rep_values

    def rep_values(self, state_id):
        if isinstance(self.type, ElementaryType):
            values = self.base_rep_values + self.get_aggregated_additional_rep_values(state_id)
            values = set(values)
            return list(values)
        return self.base_rep_values

    def load_rep_values(self, values):
        if not values:
            return
        for value in values:
            self.add_rep_value(value)

    def add_rep_value(self, value):
        if value not in self._base_rep_values:
            self._base_rep_values.append(value)

    @property
    def additional_rep_values_by_state(self):
        return self._additional_rep_values_by_state

    def add_additional_rep_values_by_state(self, state_id, values):
        # it may add invalid address to msg.sender which would cause evm error.
        if self.name != 'msg.sender':
            self._additional_rep_values_by_state[state_id] = list(values)

    def get_aggregated_additional_rep_values(self, state_id):
        res = []
        current_state_id = int(state_id, 0)
        for key, val in self.additional_rep_values_by_state.items():
            temp_state_id = int(key, 0)
            # all previous states
            if temp_state_id <= current_state_id:
                res.extend(val)
        res = set(res)
        return list(res)

    def get_w3_rep_value(self, value):
        from util import web3_value_encode
        return web3_value_encode(str(self.type), value)

    @property
    def state_var_index_read(self):
        return self._state_var_index_read

    @property
    def state_var_index_write(self):
        return self._state_var_index_write

    def set_state_var_level_index_read(self, level_dic):
        self._state_var_index_read = level_dic

    def set_state_var_level_index_write(self, level_dic):
        self._state_var_index_write = level_dic

    @property
    def used_as_index(self):
        if self.state_var_index_read and len(self.state_var_index_read.keys()) > 0:
            return True
        else:
            return False

    @property
    def used_with_constant(self):
        return self._used_with_constant

    def set_used_with_constant(self):
        self._used_with_constant = True
