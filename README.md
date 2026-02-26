# Argbox

When defining Python decorators we sometimes want to interact with the inputted arguments by their respective parameter name or position in the function's signature. This is where `argbox` comes in handy:

```python
def decorator(func):
    def wrapper(*args, **kwargs):
        ctx = Context(func, args, kwargs)
        arg_0 = ctx.get_arg(position=0)
        arg_y = ctx.get_arg(name="y")
        print(f"Parameter at position 0: {arg_0}, Parameter with name 'y': {arg_y}")
        return func(*ctx.args, **ctx.kwargs)
    return wrapper

@decorator
def func(x, y):
    pass
```

This decorator will work no matter if arguments are inputted as positional or keyword arguments; and no matter the ordering of the keyword arguments:

```python
>>> func(1, 2)
Parameter at position 0: 1, Parameter with name 'y': 2
>>> func(1, y=2)
Parameter at position 0: 1, Parameter with name 'y': 2
>>> func(x=1, y=2)
Parameter at position 0: 1, Parameter with name 'y': 2
>>> func(y=2, x=1)
Parameter at position 0: 1, Parameter with name 'y': 2
```

## Example 1

Say we want a decorator that validates the types of the inputted arguments before running the wrapped function. Without `argbox` we can make a simple version, but which will only work when arguments are passed as positional arguments:

```python
def check_types(*types):
    def wrapper(func):
        def wrapped(*args, **kwargs):
            if len(args) < len(types):
                raise ValueError(f"Expected at least {len(types)} positional arguments, got {len(args)}")
            for i, type_ in enumerate(types):
                if not isinstance(args[i], type_):
                    raise TypeError(f"Argument {i} is not of type {type_}")
            return func(*args, **kwargs)
        return wrapped
    return wrapper

@check_types(str, int)
def add(x, y):
    return x + str(y)
```

```python
>>> add("hello", 1)
hello1
>>> add("hello", y=1)
# raise ValueError
>>> add(x="hello", y=1)
# raises ValueError
>>> add(y=1, x="hello")
# raises ValueError
```

With `argbox` we can make a version that works with both positional and keyword arguments; also no matter the ordering of the keyword arguments:

```python
from argbox import Context

def check_types(*types):
    def wrapper(func):
        def wrapped(*args, **kwargs):
            ctx = Context(func, args, kwargs)
            for i, type_ in enumerate(types):
                # get argument at parameter position i
                arg = ctx.get_arg(position=i)
                if not isinstance(arg, type_):
                    raise TypeError(f"Argument {i} is not of type {type_}")
            return func(*args, **kwargs)
        return wrapped
    return wrapper

@check_types(int, str)
def add(x, y):
    return str(x) + y
```

```python
>>> add("hello", 1)
hello1
>>> add("hello", y=1)
hello1
>>> add(x="hello", y=1)
hello1
>>> add(y=1, x="hello")
hello1
```

## Example 2

Say we want a decorator that validates if the specified backend exists before running the wrapped function. Without `argbox` we can make a simple version, but which will only work when the `backend` parameter is passed as a keyword argument:

```python
def check_backend_exists(func):
    def wrapped(*args, **kwargs):
        ctx = Context(func, args, kwargs)
        if not "backend" in kwargs:
            raise ValueError("Parameter `backend` must be specified as a keyword argument")
        backend = kwargs["backend"]
        if backend == "numpy":
            if importlib.util.find_spec("numpy") is None:
                raise ImportError("Backend 'numpy' is not installed")
        return func(*ctx.args, **ctx.kwargs)
    return wrapped

@check_backend_exists
def random_array(size: int, backend="python"):
    if backend == "numpy":
        import numpy as np
        return np.random.rand(size)
    else:
        return [random.random() for _ in range(size)]
```

```python
>>> random_array(3, backend="numpy")
array([0.23532788, 0.880924  , 0.77030806])
>>> random_array(3, "numpy")
# raises ValueError
```

With `argbox` we can make a version, which works with `backend` both as a positional and keyword argument:

```python
def check_backend_exists(func):
    def wrapped(*args, **kwargs):
        ctx = Context(func, args, kwargs)
        backend = ctx.get_arg(name="backend")
        if backend == "numpy":
            if importlib.util.find_spec("numpy") is None:
                raise ImportError("Backend 'numpy' is not installed")
        return func(*ctx.args, **ctx.kwargs)
    return wrapped

@check_backend_exists
def random_array(size: int, backend="python"):
    if backend == "numpy":
        import numpy as np
        return np.random.rand(size)
    else:
        return [random.random() for _ in range(size)]
```

```python
>>> random_array(3, backend="numpy")
array([0.49507765, 0.99207232, 0.26754601])
>>> random_array(3, "numpy")
array([0.99186762, 0.96713066, 0.58288705])
```