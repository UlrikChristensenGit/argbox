import copy
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

        sig = inspect.signature(self.func)

        bound_args = sig.bind(*self.args, **self.kwargs)
        bound_args.apply_defaults()

        cnt = 0
        for arg_name, arg_value in bound_args.arguments.items():
            param = sig.parameters[arg_name]

            # handle *args when expand_vars is True: treat each item in the *args tuple as a separate argument
            if self.expand_varargs and param.kind == inspect.Parameter.VAR_POSITIONAL:
                arg_value: tuple
                for item in arg_value:
                    if position is not None and cnt == position:
                        return item
                    cnt += 1

            # handle **kwargs when expand_vars is True: treat each item in the **kwargs dict as a separate argument
            elif self.expand_varargs and param.kind == inspect.Parameter.VAR_KEYWORD:
                arg_value: dict
                for k, v in arg_value.items():
                    if name is not None and k == name:
                        return v
                    if position is not None and cnt == position:
                        return v
                    cnt += 1

            else:
                if (name is not None and arg_name == name) or (
                    position is not None and cnt == position
                ):
                    return arg_value
                cnt += 1

        if name is not None:
            raise ValueError(f"Argument with name '{name}' not found")
        else:
            raise ValueError(f"Argument with position '{position}' not found")

    def replace_arg(
        self,
        value: object,
        name: str | None = None,
        position: int | None = None,
    ):
        """Replace argument by name or position.

        (1) Replacing by name:
        Returns a new Context with the argument value corresponding the functions parameter with that name in the functions signature replaced by the new value.
        If `expand_varargs` is True, then variable arguments will be treated as if they were explicitly defined in the functions signature.
        This means:
        - Variable positional arguments are ignored, since they don't have names.
        - Variable keyword arguments are included in the search for `name`.

        (2) Replacing by position:
        Returns a new Context with the argument value corresponding to the parameter at that position in the functions signature replaced by the new value.
        If `expand_varargs` is True, then variable arguments will be treated as if they were explicitly defined in the functions signature.
        This means:
        - Variable positional arguments counts for each item in the variable positional arguments tuple.
        - Variable keyword arguments counts for each item in the variable keyword arguments dict. The ordering follows the sorting of the inputted keyword arguments (>= Python 3.6).

        Args:
            name (str | None, optional): Name of the parameter.
            position (int | None, optional): Position of the parameter.

        Returns:
            A new Context with the specified argument replaced by the new value.

        """
        if name is not None and position is not None:
            raise ValueError("Cannot specify both name and position")
        if name is None and position is None:
            raise ValueError("Must specify either name or position")

        sig = inspect.signature(self.func)

        bound_args = sig.bind(*self.args, **self.kwargs)
        bound_args.apply_defaults()

        new_bound_args = copy.deepcopy(bound_args)

        cnt = 0
        for arg_name, arg_value in bound_args.arguments.items():
            param = sig.parameters[arg_name]

            # handle *args when expand_vars is True: treat each item in the *args tuple as a separate argument
            if self.expand_varargs and param.kind == inspect.Parameter.VAR_POSITIONAL:
                arg_value: tuple
                new_arg_value = list(arg_value)
                check = False
                for i in range(len(arg_value)):
                    if position is not None and cnt == position:
                        new_arg_value[i] = value
                        check = True
                    cnt += 1
                if check:
                    new_bound_args.arguments[arg_name] = tuple(new_arg_value)
                    return Context(
                        func=self.func,
                        args=new_bound_args.args,
                        kwargs=new_bound_args.kwargs,
                        expand_varargs=self.expand_varargs,
                    )

            # handle **kwargs when expand_vars is True: treat each item in the **kwargs dict as a separate argument
            elif self.expand_varargs and param.kind == inspect.Parameter.VAR_KEYWORD:
                arg_value: dict
                new_arg_value = dict(arg_value)
                check = False
                for k in arg_value.keys():
                    if (name is not None and k == name) or (
                        position is not None and cnt == position
                    ):
                        new_arg_value[k] = value
                        check = True
                    cnt += 1
                if check:
                    new_bound_args.arguments[arg_name] = new_arg_value
                    return Context(
                        func=self.func,
                        args=new_bound_args.args,
                        kwargs=new_bound_args.kwargs,
                        expand_varargs=self.expand_varargs,
                    )

            else:
                if (name is not None and arg_name == name) or (
                    position is not None and cnt == position
                ):
                    new_bound_args.arguments[arg_name] = value
                    return Context(
                        func=self.func,
                        args=new_bound_args.args,
                        kwargs=new_bound_args.kwargs,
                        expand_varargs=self.expand_varargs,
                    )
                cnt += 1

        if name is not None:
            raise ValueError(f"Argument with name '{name}' not found")
        else:
            raise ValueError(f"Argument with position '{position}' not found")

    def replace_args(self, mapping: dict[str | int, object]):
        """Replace multiple arguments by name or position.

        This is a helper method that calls `replace_arg` multiple times to replace multiple arguments at once.

        Args:
            mapping (dict[str | int, object]): A mapping of argument names or positions to their new values.

        Returns:
            A new Context with the specified arguments replaced by the new values.
        """
        new_ctx = self
        for key, value in mapping.items():
            if isinstance(key, int):
                new_ctx = new_ctx.replace_arg(value=value, position=key)
            elif isinstance(key, str):
                new_ctx = new_ctx.replace_arg(value=value, name=key)
            else:
                raise ValueError(
                    f"Invalid key type '{type(key)}' in mapping. Must be str or int."
                )
        return new_ctx
