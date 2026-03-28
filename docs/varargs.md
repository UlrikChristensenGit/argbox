# Handling variable parameters

For a function with variable parameters, the default in `argbox` is to treat these as a **single parameter** of type `tuple` (for \*args) or `dict` (for \*\*kwargs):

```py
def f(*args, **kwargs):
    pass

ctx = argbox.Context(
    func=f,
    args=(1,2),
    kwargs={"z": 3, "w": 4},
)

>>> ctx.get_arg(position=0)
(1,2)
>>> ctx.get_arg(name="kwargs")
{z: 3, w: 4}
```

However, you might want to treat variable parameters in an expanded fashion: i.e. as **n parameters**, where n is the number of inputted \*args or \*\*kwargs:

```py hl_lines="5"
>>> ctx = argbox.Context(
    func=f,
    args=(1,2),
    kwargs={"z": 3, "w": 4},
    expand_varargs=True, # (1)!
)
>>> ctx.get_arg(position=0)
1
>>> ctx.get_arg(name="z")
3
```

1.  Use `expand_varargs=True` to simulate, that the variable input arguments were explicitly defined in the functions signature.
