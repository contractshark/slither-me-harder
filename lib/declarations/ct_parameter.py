from collections import defaultdict
import definitions


class CtParameter:
    def __init__(self, parameter, i, state_value_map):
        self._original_parameter = parameter
        self._name = ''
        if '.' in parameter.name:
            self._name = parameter.name.replace('.', '_')
        elif parameter.name == '':
            self._name = 'MISSING_NAME_' + str(i)
        else:
            self._name = parameter.name

        self._base_values = parameter.base_rep_values  # list of value
        self._state_based_rep_values = state_value_map  # map, state => values

        self._rep_values = None  # list of values
        self._index_state_mapper = defaultdict(set)  # map, index => list of states

        self._set_rep_values()
        self._set_index_mapper()

    def __repr__(self):
        return f'{self.original_parameter.name}  => {str(self._rep_values)}'

    def __str__(self):
        return f'{self.original_parameter.name}  => {str(self._rep_values)}'

    def get_value_from_index(self, index):
        return self._rep_values[index]

    def get_states_from_index(self, index):
        return self._index_state_mapper[index]

    def _get_valid_indexes_from_state(self, state):
        res = []
        for index, states in self._index_state_mapper.items():
            if not states:
                res.append(index)
            elif state in states:
                res.append(index)
        return res

    def get_constraints_from_state(self, state, state_index):
        left_side = f'{definitions.CT_STATE_VAR_ID} = "{state_index}"'
        right_side_list = []
        valid_indexes = self._get_valid_indexes_from_state(state)
        for index in valid_indexes:
            right_side_list.append(f'{self.name} = "{index}"')

        right_side = f'({" || ".join(right_side_list)})'
        return f'{left_side} => {right_side}'

    # @property
    # def rep_values(self):
    #     return self._rep_values

    @property
    def name(self):
        return self._name

    @property
    def rep_values_indexes(self):
        res = []
        for i in range(len(self._rep_values)):
            res.append(i)
        return res

    @property
    def original_parameter(self):
        return self._original_parameter
    #
    # @property
    # def base_values(self):
    #     return self._base_values
    #
    @property
    def state_based_rep_values_dic(self):
        return self._state_based_rep_values

    @property
    def state_based_rep_values_aggregated(self):
        # likely useless
        res = []
        for values in self.state_based_rep_values_dic.values():
            for value in values:
                if value not in res:
                    res.append(value)
        return res

    def _set_rep_values(self):
        res = self._base_values
        # state based values should be distinct from base values
        # ensure this, otherwise, hell will break loose

        # use list instead of set, because arrays are not hashable.
        for val in self.state_based_rep_values_aggregated:
            if val not in res:
                res.append(val)
        self._rep_values = res

    def _find_appeared_states_based_on_value(self, val):
        res = set()
        for state, values in self._state_based_rep_values.items():
            if val in values:
                res.add(state)
        return res

    def _set_index_mapper(self):
        for i, val in enumerate(self._rep_values):
            states = self._find_appeared_states_based_on_value(val)
            self._index_state_mapper[i] = states


