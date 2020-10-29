import z3
from slither.core.expressions.binary_operation import BinaryOperation
from slither.core.expressions.identifier import Identifier
from slither.core.expressions.literal import Literal
from slither.core.expressions.tuple_expression import TupleExpression
from slither.core.expressions.unary_operation import UnaryOperation


def get_z3_vars(op, dic):
    """
    # Not complete, not used.
    Takes a slither expression and a dictionary, creates the Z3 objects of all variables
    involved within the expression.

    The following link contains all types of expressions that need to be parsed.
    https://github.com/crytic/slither/tree/master/slither/core/expressions

    Future work to handle more types of expressions is still needed.
    """
    if isinstance(op, BinaryOperation):
        get_z3_vars(op.expression_left, dic)
        get_z3_vars(op.expression_right, dic)
    elif isinstance(op, UnaryOperation):
        get_z3_vars(op.expression, dic)
    elif isinstance(op, TupleExpression):
        get_z3_vars(op.expression_left, dic)
        get_z3_vars(op.expression, dic)
    elif isinstance(op, Identifier):
        dic[op.value.name] = z3.Int(op.value.name)
    elif isinstance(op, Literal):
        pass
    else:
        raise Exception("Unhandled Operation")






