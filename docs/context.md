# The Context class

The core of `argbox` is the `Context` class, which encapsulates a given function with a set of passed arguments.

## Retrieving arguments
Using the `Context` class, you can retrieve arguments by their respective parameter names or positions. In a decorator, this can be used to validate the input data before running the base function: 

```py hl_lines="4 5"
def binary_operator(func):
    def wrapper(*args, **kwargs):
        ctx = argbox.Context(func, args, kwargs)
        left = ctx.get_arg(position=0)
        right = ctx.get_arg(position=1)
        
        # ensure types are the same
        assert type(left) == type(right)
        
        return func(*ctx.args, **ctx.kwargs)
    return wrapper

@binary_operator
def add(x, y, mod=None):
    return (x + y) % mod if mod is not None else x + y
```

## Replacing arguments
Using the `Context` class, you can also replace arguments by their respective parameter names or positions. In a decorator, this can be used to preprocess the input data before running the base function:

``` py hl_lines="8 9 10 11"
def binary_operator(func):
    def wrapper(*args, **kwargs):
        ctx = argbox.Context(func, args, kwargs)
        left = ctx.get_arg(position=0)
        right = ctx.get_arg(position=1)

        # cast operators to floats
        new_ctx = ctx.replace_args({
            0: float(left),
            1: float(right),
        })

        return func(*new_ctx.args, **new_ctx.kwargs)
    return wrapper

@binary_operator
def add(x, y, mod=None):
    return (x + y) % mod if mod is not None else x + y
```