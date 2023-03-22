from functools import reduce

def chain(*funcs):
    """Pipeline a series of functions"""
    def chained_call(arg):
        return reduce(lambda r, f: f(r), funcs, arg)

    return chained_call
