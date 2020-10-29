from .operation import Operation


class UnaryOperation(Operation):
    """
    This class is still yet to be utilized.
    Currently, we are using slither UnaryOperation directly from slither.

    Finished.
    """

    def __init__(self):
        super().__init__()
        self.var = None
