import inspect
from typing import Callable


class Context:
    def __init__(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
        expand_varargs: bool = False,
    ):
        """Class representing the context of a function call, with methods to
        interact with the arguments passed to that function.

        Args:
            func (Callable): The function being called.
            args (tuple): Positional arguments passed to the function.
            kwargs (dict): Keyword arguments passed to the function.
            expand_varargs (bool): Whether to treat variable arguments as if
                they were explicitly defined in the functions signature.
        """
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.expand_varargs = expand_varargs

    def _get_arg_by_name(self, name: str):
        sig = inspect.signature(self.func)

        bound_args = sig.bind(*self.args, **self.kwargs)
        bound_args.apply_defaults()

        if name in bound_args.arguments:
            parameter = sig.parameters[name]
            if not (
                self.expand_varargs
                and parameter.kind
                in [inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD]
            ):
                return bound_args.arguments[name]

        for param in sig.parameters.values():
            if self.expand_varargs and param.kind == inspect.Parameter.VAR_KEYWORD:
                var_kwargs = bound_args.arguments.get(param.name, {})
                if name in var_kwargs:
                    return var_kwargs[name]

        raise ValueError(f"Argument with name '{name}' not found.")

    def _get_arg_by_position(self, position: int):
        sig = inspect.signature(self.func)
        bound_args = sig.bind(*self.args, **self.kwargs)
        bound_args.apply_defaults()

        def iter_args():
            for arg_name, arg_value in bound_args.arguments.items():
                param = sig.parameters[arg_name]
                if (
                    self.expand_varargs
                    and param.kind == inspect.Parameter.VAR_POSITIONAL
                ):
                    arg_value: tuple
                    for item in arg_value:
                        yield item
                elif (
                    self.expand_varargs and param.kind == inspect.Parameter.VAR_KEYWORD
                ):
                    arg_value: dict
                    for item in arg_value.values():
                        yield item
                else:
                    yield arg_value

        for i, arg in enumerate(iter_args()):
            if i == position:
                return arg

        raise ValueError(f"Argument at position {position} not found.")

    def get_arg(
        self,
        name: str | None = None,
        position: int | None = None,
    ):
        """Get argument by name or position.

        (1) Getting by name:
        Returns the argument value corresponding the functions parameter with
        that name in the functions signature.
        If `expand_varargs` is True, then variable arguments will be treated
        as if they were explicitly defined in the functions signature.
        This means:
        - Variable positional arguments are ignored, since they don't have
          names.
        - Variable keyword arguments are included in the search for `name`.

        (2) Getting by position:
        Returns the argument value corresponding to the parameter at that
        position in the functions signature.
        If `expand_varargs` is True, then variable arguments will be treated
        as if they were explicitly defined in the functions signature.
        This means:
        - Variable positional arguments counts for each item in the variable
          positional arguments tuple.
        - Variable keyword arguments counts for each item in the variable
          keyword arguments dict. The ordering follows the sorting of the
          inputted keyword arguments (>= Python 3.6).

        Args:
            name (str | None, optional): Name of the parameter.
            position (int | None, optional): Position of the parameter.

        Returns:
            Value of the argument with the specified name or position.
        """
        if name is not None and position is not None:
            raise ValueError("Cannot specify both name and position")
        if name is None and position is None:
            raise ValueError("Must specify either name or position")

        if name is not None:
            return self._get_arg_by_name(name)
        else:
            return self._get_arg_by_position(position)
