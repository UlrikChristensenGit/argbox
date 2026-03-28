from typing import Callable

from argbox.context import Context
from argbox.dispatching import dispatcher
from argbox.preprocessing import preprocessor


@dispatcher
def dispatch_on_type(*types: type, **kw_types: type):
    """Dispatch based on the type of each input argument.

    Args:
        *types: Types that must be valid for the parameter(s) with positions
            corresponding to the index in the tuple.
        **kw_types: Types that must be valid for parameter(s) with names
            corresponding to the keys in the dictionary.

    Example (1): Using parameter positions:

        @dispatch_on_type
        def scale(scalar, vector):
            ...

        @scale.register(float, float)
        def _(scalar, vector):
            return scalar * vector

        @scale.register(float, list)
        def _(scalar, vector):
            return [scalar * comp for comp in vector]

    Example (2): Using parameter names:

        @dispatch_on_type
        def scale(scalar, vector):
            ...

        @scale.register(vector=float, scalar=float)
        def _(scalar, vector):
            return scalar * vector

        @scale.register(vector=list, scalar=int)
        def _(scalar, vector):
            return [scalar * comp for comp in vector]

    """

    def validator(ctx: Context) -> bool:
        ctx.expand_varargs = True

        # check arguments by position
        for i, type_ in enumerate(types):
            arg = ctx.get_arg(position=i)
            if not isinstance(arg, type_):
                return False

        # check arguments by name
        for name, type_ in kw_types.items():
            arg = ctx.get_arg(name=name)
            if not isinstance(arg, type_):
                return False

        return True

    return validator


@dispatcher
def dispatch_on_rule(*rules: Callable, **kw_rules: Callable):
    """
    Dispatch based on the result of a rule applied to each input argument.

    Args:
        *rules: Rule to check for the parameter(s) with positions corresponding to the index in the tuple.
        **kw_rules: Rule to check for parameter(s) with names corresponding to the keys in the dictionary.

    Example (1): Using parameter positions:

        @dispatch_on_rule
        def divide(num, denom):
            ...

        @divide.register(
            lambda n: True,
            lambda d: d != 0,
        )
        def _(num, denom):
            return num / denom

        @divide.register(
            lambda n: n != 0,
            lambda d: d == 0,
        )
        def _(num, denom):
            return float('inf')

    Example (2): Using parameter names:

        @dispatch_on_rule
        def divide(num, denom):
            ...

        @divide.register(
            denom=lambda d: d != 0,
            num=lambda n: True,
        )
        def _(num, denom):
            return num / denom

        @divide.register(
            denom=lambda d: d == 0,
            num=lambda n: n != 0,
        )
        def _(num, denom):
            return float('inf')
    """

    def validator(ctx: Context) -> bool:
        ctx.expand_varargs = True

        # check arguments by position
        for i, rule in enumerate(rules):
            arg = ctx.get_arg(position=i)
            if not rule(arg):
                return False

        # check arguments by name
        for name, rule in kw_rules.items():
            arg = ctx.get_arg(name=name)
            if not rule(arg):
                return False

        return True

    return validator


def preprocess_by_transformations(
    *transformations: Callable, **kw_transformations: Callable
):
    @preprocessor
    def modifier(ctx: Context) -> Context:
        ctx.expand_varargs = True

        new_ctx = ctx

        # apply transformations to arguments by position
        for i, transformation in enumerate(transformations):
            new_ctx = new_ctx.transform_arg(transformation, position=i)

        # apply transformations to arguments by name
        for name, transformation in kw_transformations.items():
            new_ctx = new_ctx.transform_arg(transformation, name=name)

        return new_ctx

    return modifier
