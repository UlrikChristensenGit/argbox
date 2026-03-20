import pytest

from argbox import Context


def replace(mapping: dict[str | int], expand_varargs: bool = False):
    """Helper that replaces an argument by position and then gets all arguments by position."""

    def wrapper(func):
        def wrapped(*args, **kwargs):
            ctx = Context(func, args, kwargs, expand_varargs)
            new_ctx = ctx.replace_args(mapping)
            return func(*new_ctx.args, **new_ctx.kwargs)

        return wrapped

    return wrapper


def test_replace_arg_positional_or_keyword():
    @replace(mapping={0: 10, "b": 15})
    def func(a, b):
        return a + b

    expected = 25

    assert func(1, 2) == expected
    assert func(a=1, b=2) == expected
    assert func(1, b=2) == expected
    assert func(b=2, a=1) == expected
    assert func(*[1, 2]) == expected
    assert func(**{"a": 1, "b": 2}) == expected


def test_replace_arg_positional_or_keyword_with_defaults():
    @replace(mapping={0: 10, "b": 15})
    def func(a=1, b=2):
        return a + b

    expected = 25

    assert func() == expected
    assert func(1) == expected
    assert func(1, 2) == expected
    assert func(a=1) == expected
    assert func(b=2) == expected
    assert func(a=1, b=2) == expected
    assert func(b=2, a=1) == expected
    assert func(1, b=2) == expected
    assert func(*[1, 2]) == expected
    assert func(**{"a": 1, "b": 2}) == expected
    assert func(**{"b": 2, "a": 1}) == expected


def test_replace_arg_positional_only():
    @replace(mapping={0: 10, "b": 15})
    def func(a, b, /):
        return a + b

    expected = 25

    assert func(1, 2) == expected
    assert func(*[1, 2]) == expected


def test_replace_arg_positional_only_with_defaults():
    @replace(mapping={0: 10, "b": 15})
    def func(a=1, b=2, /):
        return a + b

    expected = 25

    assert func() == expected
    assert func(1) == expected
    assert func(1, 2) == expected
    assert func(*[1, 2]) == expected


def test_replace_arg_keyword_only():
    @replace(mapping={0: 10, "b": 15})
    def func(*, a, b):
        return a + b

    expected = 25

    assert func(a=1, b=2) == expected
    assert func(b=2, a=1) == expected
    assert func(**{"a": 1, "b": 2}) == expected
    assert func(**{"b": 2, "a": 1}) == expected


def test_replace_arg_keyword_only_with_defaults():
    @replace(mapping={0: 10, "b": 15})
    def func(*, a=1, b=2):
        return a + b

    expected = 25

    assert func() == expected
    assert func(a=1) == expected
    assert func(b=2) == expected
    assert func(a=1, b=2) == expected
    assert func(b=2, a=1) == expected
    assert func(**{"a": 1, "b": 2}) == expected
    assert func(**{"b": 2, "a": 1}) == expected


def test_replace_arg_varargs():
    @replace(mapping={0: (10, 20), "kwargs": {"a": 5, "b": 15}})
    def func(*args, **kwargs):
        return sum(args) + sum(kwargs.values())

    expected = 30 + 20

    assert func(1, 2, a=1, b=2) == expected
    assert func(1, 2, b=2, a=1) == expected
    assert func(*[1, 2], **{"a": 1, "b": 2}) == expected
    assert func(*[1, 2], **{"b": 2, "a": 1}) == expected


def test_replace_arg_varargs_expanded():
    @replace(mapping={0: 10, 1: 20, "a": 5, "b": 15}, expand_varargs=True)
    def func(*args, **kwargs):
        return sum(args) + sum(kwargs.values())

    expected = 30 + 20

    assert func(1, 2, a=3, b=4) == expected
    assert func(1, 2, b=3, a=4) == expected


def test_replace_arg_non_existent_position_error():
    @replace(mapping={3: 100}, expand_varargs=True)
    def func(a, b):
        pass

    with pytest.raises(ValueError):
        func(1, 2)


def test_replace_arg_non_existent_name_error():
    @replace(mapping={"c": 100})
    def func(a, b):
        pass

    with pytest.raises(ValueError):
        func(1, 2)


def test_replace_arg_varargs_expanded_non_existent_position_error():
    @replace(mapping={4: 100}, expand_varargs=True)
    def func(*args, **kwargs):
        pass

    with pytest.raises(ValueError):
        func(1, 2, a=1, b=2)


def test_replace_arg_varargs_expanded_non_existent_name_error():
    @replace(mapping={"c": 100}, expand_varargs=True)
    def func(*args, **kwargs):
        pass

    with pytest.raises(ValueError):
        func(1, 2, a=1, b=2)
