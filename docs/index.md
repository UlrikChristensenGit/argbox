<style>
h1#overview {
    position: absolute;
    width: 0;
    height: 0;
    overflow: hidden;
    clip: rect(0 0 0 0 0);
    white-space: nowrap;
  }
</style>

# Overview

![alt text](logo.png){: style="transform: scale(0.5); align: center ; display: block; margin-left: auto; margin-right: auto;"}

`argbox` is a Python package for interacting with the arguments passed to a function by their respective parameter name or position in the function's signature:

```py title="Decorator example" hl_lines="5 6 7"
import argbox

def my_decorator(func):
    def wrapper(*args, **kwargs):
        ctx = argbox.Context(func, args, kwargs) # (1)!
        param_0_arg = ctx.get_arg(position=0) # (2)!
        param_y_arg = ctx.get_arg(name="y") # (3)!
        print(f"Parameter 0={param_0_arg} y={param_y_arg}")
        return func(*ctx.args, **ctx.kwargs)
    return wrapper

@my_decorator
def func(x, y):
    pass
```

1.  Create an context for a given function and passed arguments
2.  Retrieve the argument corresponding to parameter with position 0
3.  Retrieve the argument corresponding to the parameter with name 'y'

The decorated function behaves the same no matter if arguments are inputted as positional or keyword arguments; and no matter the ordering of the keyword arguments:

```py
>>> func(10, 20)
10 20
>>> func(10, y=20)
10 20
>>> func(x=10, y=20)
10 20
>>> func(y=20, x=10)
10 20 # (1)!
```

1.  Wait, shouldn't this print `20 20`, since the 0th argument is now `20`? No! The entire point of`argbox` is to use the names and position of the *parameters* - not the passed arguments.
