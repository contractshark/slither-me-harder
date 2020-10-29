from slither.core.declarations.modifier import Modifier as Slither_Modifier

from .function_call import FunctionCall


class Modifier(FunctionCall):
    def __init__(self, modifier: Slither_Modifier, parent_contract):
        super().__init__()
        self._functions_used = set()

        self._setter(modifier, parent_contract)

    ###################################################################################
    ###################################################################################
    # region => public getters
    ###################################################################################
    ###################################################################################

    @property
    def functions_used(self):
        return list(self._functions_used)

    @property
    def summary(self):
        """
        For returning the summary of the modifier.

        Finished.
        """
        res = []
        res.append(f'Modifier: {self._signature}')

        res.append(f'\tRequires:')
        for r in self._requires:
            res.append(f'\t\t{str(r)}')

        v = ''
        for s in self.parameters:
            v += s.name + ', '
        res.append(f'\tParameters: {v[:-2]}')

        v = ''
        for s in self._state_variables_read:
            v += s.name + ', '
        res.append(f'\tState Vars Read: {v[:-2]}')

        v = ''
        for s in self._state_variables_written:
            v += s.name + ', '
        res.append(f'\tState Vars Written: {v[:-2]}')

        v = ''
        for s in self._local_variables_read:
            v += s.name + ', '
        res.append(f'\tLocal Vars Read: {v[:-2]}')

        v = ''
        for s in self._local_variables_written:
            v += s.name + ', '
        res.append(f'\tLocal Vars Written: {v[:-2]}')

        return '\n'.join(res)

    def __str__(self):
        return self._signature

    def __repr__(self):
        return self._signature

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

    def _setter(self, modifier: Slither_Modifier, parent_contract):
        """
        Setting values when initializing

        Finished.
        """
        self._function_call_setter(modifier, parent_contract)

    # end of region
    ###################################################################################
    ###################################################################################
    # region => private functions
    ###################################################################################
    ###################################################################################
