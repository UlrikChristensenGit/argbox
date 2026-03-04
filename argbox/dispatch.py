import functools
import types
from typing import Callable, Generic, ParamSpec, TypeVar

from argbox.context import Context

# Base function parameters and return type
BP = ParamSpec("BP")
BR = TypeVar("BR")

# Validator function parameters
VFP = ParamSpec("VFP")

# Type aliases (note: we cannot type alias some of the other
# specifications, such as validator factory, since they use type vars)
Validator = Callable[[Context], bool]


class DispatchedFunction(Generic[BP, BR, VFP]):
    def __init__(
        self,
        base: Callable[BP, BR],
        validator_factory: Callable[VFP, Validator],
    ) -> None:
        self.is_class_method = isinstance(base, classmethod)
        self.is_static_method = isinstance(base, staticmethod)
        if self.is_class_method or self.is_static_method:
            self.base = base.__func__
        else:
            self.base = base
        self.validator_factory = validator_factory
        self.lookup_table: list[tuple[Validator, Callable[BP, BR]]] = []

    def register(
        self,
        *args: VFP.args,
        **kwargs: VFP.kwargs,
    ) -> Callable[[Callable[BP, BR]], Callable[BP, BR]]:
        def wrapper(implementation: Callable[BP, BR]) -> Callable[BP, BR]:
            validator = self.validator_factory(*args, **kwargs)
            self.lookup_table.append((validator, implementation))
            return implementation

        return wrapper

    def __call__(
        self,
        *args: BP.args,
        **kwargs: BP.kwargs,
    ) -> BR:
        ctx = Context(self.base, args, kwargs, expand_varargs=True)
        for validator, implementation in self.lookup_table:
            if validator(ctx):
                return implementation(*args, **kwargs)

        raise NotImplementedError(
            f"No implementation found for arguments {args} "
            f"and keyword arguments {kwargs}"
        )

    def __get__(self, instance, owner):
        if self.is_class_method:
            return functools.partial(self.__call__, owner)
        elif self.is_static_method:
            return self.__call__
        else:
            return functools.partial(self.__call__, instance)


def dispatcher(
    validator_factory: Callable[VFP, Validator],
) -> Callable[[Callable[BP, BR]], DispatchedFunction[BP, BR, VFP]]:
    def wrapper(base_func: Callable[BP, BR]) -> DispatchedFunction[BP, BR, VFP]:
        return DispatchedFunction(base_func, validator_factory)

    return wrapper
