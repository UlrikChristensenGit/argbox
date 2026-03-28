from typing import Callable, ParamSpec, TypeVar

from argbox.context import Context

# Base function parameters and return type
BP = ParamSpec("BP")
BR = TypeVar("BR")

Modifier = Callable[[Context], Context]


def preprocessor(
    modifier: Modifier,
):
    def wrapper(base_func: Callable[BP, BR]) -> Callable[BP, BR]:
        def preprocessed_function(*args: BP.args, **kwargs: BP.kwargs) -> BR:
            ctx = Context(base_func, args, kwargs)
            new_ctx = modifier(ctx)
            return base_func(*new_ctx.args, **new_ctx.kwargs)

        return preprocessed_function

    return wrapper
