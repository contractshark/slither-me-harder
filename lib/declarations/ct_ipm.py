from collections import defaultdict
from .ct_parameter import CtParameter
from .ct_tc import CtTc
import definitions
from util import get_boundary_values
from slither.core.solidity_types.elementary_type import ElementaryType


def get_index_values_from_state(state, function):
    res = defaultdict(list)  # Parameter => list(values)
    if not state:
        return res
    index_values = state.previous_index_values_dic if state else dict()  # data_type => level => StateVariableSolc => list(value)

    # for param in each function param
    for param in function.parameters:
        if param.name == 'msg.sender':
            continue
        state_var_index_read = param.state_var_index_read  # level => set(StateVariableSolc)
        if state_var_index_read and param.type in index_values.keys():
            # for the current state, the data type, levels it has values on
            levels = index_values[param.type]
            for param_level, param_SVs_set in state_var_index_read.items():
                if param_level in levels.keys():
                    for param_sv in param_SVs_set:
                        if param_sv in levels[param_level].keys():
                            for value in levels[param_level][param_sv]:
                                # ensure only new values from the base rep values of the parameter is added
                                if value not in param.base_rep_values:
                                    if type(param.type) == ElementaryType and 'int' in param.type.name:
                                        min_val, max_val = get_boundary_values(param.type, param.name)
                                        if min_val <= value <= max_val:
                                            if value not in res[param]:
                                                res[param].append(value)
                                    else:
                                        if value not in res[param]:
                                            res[param].append(value)
    return res


class CtIpm:
    def __init__(self, function):
        self._function = function
        self._parameters = dict()  # good to go p_name as key, ct_param as value

        self._rep_states = []
        self._setter()

    def __repr__(self):
        res = []
        for param in self._parameters.values():
            res.append(param)

        # for state in self._rep_states:
        #     res.append(state)

        return '\n'.join(res)

    def __str__(self):
        res = []
        for param in self._parameters.values():
            res.append(str(param))

        # for state in self._rep_states:
        #     res.append(str(state))

        return '\n'.join(res)

    @property
    def function(self):
        return self._function

    @property
    def rep_states(self):
        return self._rep_states

    @property
    def rep_states_indexes(self):
        res = []
        for i in range(len(self.rep_states)):
            res.append(i)

        return res

    @property
    def ct_parameters_dic(self):
        return self._parameters

    def _setter(self):
        temp = defaultdict(lambda: defaultdict(list))  # Parameter => state => set(value)

        if not self.function.rep_states:
            self._rep_states.append(None)

        for state in self.function.rep_states:
            self._rep_states.append(state)
            additional_index_values = get_index_values_from_state(state, self.function)
            for param, values in additional_index_values.items():
                temp[param][state] = values

        for i, param in enumerate(self.function.parameters):
            new_ct_param = CtParameter(param, i, temp[param])
            self._parameters[new_ct_param.name] = new_ct_param

    def _configure_acts_constraints(self):
        res = definitions.ACTS_GATEWAY.jvm.java.util.ArrayList()
        for i, state in enumerate(self.rep_states):
            for ct_param in self.ct_parameters_dic.values():
                constraint_str = ct_param.get_constraints_from_state(state, i)
                constraint = definitions.ACTS_GATEWAY.jvm.java.util.ArrayList()
                constraint.append(constraint_str)
                constraint.append(definitions.CT_STATE_VAR_ID)
                constraint.append(ct_param.name)
                res.append(constraint)
                # print(f'Constraint: "{constraint_str}"  {definitions.CT_STATE_VAR_ID}   {ct_param.original_parameter.name}')
        return res

    def get_ct_tc(self):
        if not self.ct_parameters_dic:
            # handle fallback that has no parameter
            return []
        build_sut = definitions.ACTS_GATEWAY.entry_point
        acts_config = self._configure_acts_ipm()
        acts_constraints = self._configure_acts_constraints()
        try:
            tc_str = build_sut.initialCT(self.function.canonical_name, acts_config, acts_constraints)
        except:
            return []
        return self._tc_str_to_tc(tc_str)

    def _tc_str_to_tc(self, tc_str):
        # list of CtTc objects, .state attribute returns the state, .tc returns the actual tc with p_name as key
        res = []
        tc_list = tc_str.strip().split('\n')
        keys = tc_list[0].replace('"', '').strip().split(' ')
        for i in range(1, len(tc_list)):
            tc = {}
            tc_line = tc_list[i].strip().split(' ')
            tc_state = None
            for j in range(len(keys)):
                key = keys[j]
                if key == definitions.CT_STATE_VAR_ID:
                    tc_state = self.rep_states[int(tc_line[j])]
                else:
                    # ACTS constraints cannot have parameters with . in its name, e.g. "msg.sender"
                    origin_param_name = self._parameters[key].original_parameter.name
                    tc[origin_param_name] = self._get_value_from_p_name_and_index(key, int(tc_line[j]))

            ct_tc = CtTc(tc_state)
            ct_tc.set_tc(tc)
            res.append(ct_tc)
        return res

    def _get_value_from_p_name_and_index(self, p_name, index):
        # get transaction object if param is state
        if p_name == definitions.CT_STATE_VAR_ID:
            return
        else:
            # get param value for non-state params
            return self._parameters[p_name].get_value_from_index(index)

    def _configure_acts_ipm(self):
        acts_config = definitions.ACTS_GATEWAY.jvm.java.util.ArrayList()

        # state variable
        p_content = definitions.ACTS_GATEWAY.jvm.java.util.ArrayList()
        p_content.append(definitions.CT_STATE_VAR_ID)
        for i in self.rep_states_indexes:
            p_content.append(str(i))
        acts_config.append(p_content)

        # other variable
        for ct_param in self.ct_parameters_dic.values():
            p_content = definitions.ACTS_GATEWAY.jvm.java.util.ArrayList()
            p_content.append(ct_param.name)
            for i in ct_param.rep_values_indexes:
                p_content.append(str(i))

            acts_config.append(p_content)

        return acts_config








