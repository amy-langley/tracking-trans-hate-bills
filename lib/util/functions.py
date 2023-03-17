from functools import reduce

def chain(*funcs):
    def chained_call(arg):
        return reduce(lambda r, f: f(r), funcs, arg)

    return chained_call
