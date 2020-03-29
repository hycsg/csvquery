from datetime import datetime

class Operators:
    equal = "eq"
    not_equal = "neq"
    less_than = "lt"
    greater_than = "gt"
    less_than_or_equal = "lte"
    greater_than_or_equal = "gte"
    inside = "in"
    _not = "not"
    _and = "and"
    _or = "or"

    comparison = "comparison"

class Comparisons:
    integers = lambda a, b: int(a) < int(b)
    floats = lambda a, b: float(a) < float(b)
    strings = lambda a, b: a < b

    default = floats

    @staticmethod
    def get_date_comparison(format_string):
        return lambda a, b: datetime.strptime(a, format_string) < datetime.strptime(b, format_string)

operator_functions = {
    Operators.equal                 :   lambda t, v, c: t == v,
    Operators.not_equal             :   lambda t, v, c: t != v,
    Operators.less_than             :   lambda t, v, c: c(t, v),
    Operators.greater_than          :   lambda t, v, c: c(v, t),
    Operators.less_than_or_equal    :   lambda t, v, c: not c(v, t),
    Operators.greater_than_or_equal :   lambda t, v, c: not c(t, v),
    Operators.inside                :   lambda t, v, c: t in [str(x) for x in v],
    Operators._not                  :   lambda t, v, c: not operator_functions[list(v)[0]](t, v[list(v)[0]], c),
    Operators._and                  :   lambda t, v, c: not (False in [operator_functions[list(d)[0]](t, d[list(d)[0]], c) for d in v]),
    Operators._or                   :   lambda t, v, c: True in [operator_functions[list(d)[0]](t, d[list(d)[0]], c) for d in v],
}
