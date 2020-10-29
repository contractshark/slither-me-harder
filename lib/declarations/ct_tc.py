class CtTc:
    def __init__(self, state):
        self._state = state
        self._tc = dict()

    @property
    def state(self):
        return self._state

    @property
    def tc(self):
        return self._tc

    def set_tc(self, tc):
        self._tc = tc