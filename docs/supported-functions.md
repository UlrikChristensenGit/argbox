# Supported functions

`argbox` supports the following function definition and calling patterns:

## Function definitions
| Type | Example |
|--|--|
| Positional-or-keyword arguments | `def f(a, b=1)` |
| Positional-only arguments | `def f(a, b=1, /)` |
| Keyword-only arguments | `def f(*, a, b=1)` | 
| Variable positional and keyword arguments | `def f(*args, **kwargs)` |
| Async functions | `async def f(a, b=1)` |
| Any combination of the above | `def f(a, b=1, /, c=2, *args, d, e=3, **kwargs)` |

## Function calling
| Type | Example |
|--|--|
| Positional arguments | `f(1, 2)`
| Keyword arguments | `f(a=1, b=2)` (ordering is not needed, so `f(b=2, a=1)` works the same)
| Any combination of the above | `f(1, b=2)`