import pytest

from argbox import Context


def return_map(names: list[str], expand_varargs: bool = False):
    def wrapper(func):
        def wrapped(*args, **kwargs):
            ctx = Context(func, args, kwargs, expand_varargs)
            mapping = {name: ctx.get_arg(name) for name in names}
            return mapping

        return wrapped

    return wrapper


def test_get_arg_by_name_positional_or_keyword():
    @return_map(names=["a", "b"])
    def func(a, b):
        pass

    expected = {"a": 1, "b": 2}

    assert func(1, 2) == expected
    assert func(a=1, b=2) == expected
    assert func(1, b=2) == expected
    assert func(b=2, a=1) == expected
    assert func(*[1, 2]) == expected
    assert func(**{"a": 1, "b": 2}) == expected


def test_get_arg_by_name_positional_or_keyword_with_defaults():
    @return_map(names=["a", "b"])
    def func(a=1, b=2):
        pass

    expected = {"a": 1, "b": 2}

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


def test_get_arg_by_name_positional_only():
    @return_map(names=["a", "b"])
    def func(a, b, /):
        pass

    expected = {"a": 1, "b": 2}

    assert func(1, 2) == expected
    assert func(*[1, 2]) == expected


def test_get_arg_by_name_positional_only_with_defaults():
    @return_map(names=["a", "b"])
    def func(a=1, b=2, /):
        pass

    expected = {"a": 1, "b": 2}

    assert func() == expected
    assert func(1) == expected
    assert func(1, 2) == expected
    assert func(*[1, 2]) == expected


def test_get_arg_by_name_keyword_only():
    @return_map(names=["a", "b"])
    def func(*, a, b):
        pass

    expected = {"a": 1, "b": 2}

    assert func(a=1, b=2) == expected
    assert func(b=2, a=1) == expected
    assert func(**{"a": 1, "b": 2}) == expected
    assert func(**{"b": 2, "a": 1}) == expected


def test_get_arg_by_name_keyword_only_with_defaults():
    @return_map(names=["a", "b"])
    def func(*, a=1, b=2):
        pass

    expected = {"a": 1, "b": 2}

    assert func() == expected
    assert func(a=1) == expected
    assert func(b=2) == expected
    assert func(a=1, b=2) == expected
    assert func(b=2, a=1) == expected
    assert func(**{"a": 1, "b": 2}) == expected
    assert func(**{"b": 2, "a": 1}) == expected


def test_get_arg_by_name_varargs():
    @return_map(names=["args", "kwargs"])
    def func(*args, **kwargs):
        pass

    expected = {"args": (1, 2), "kwargs": {"a": 1, "b": 2}}

    assert func(1, 2, a=1, b=2) == expected
    assert func(1, 2, b=2, a=1) == expected
    assert func(*[1, 2], **{"a": 1, "b": 2}) == expected
    assert func(*[1, 2], **{"b": 2, "a": 1}) == expected


def test_get_arg_by_name_varargs_expanded():
    @return_map(names=["a", "b"], expand_varargs=True)
    def func(*args, **kwargs):
        pass

    expected = {"a": 1, "b": 2}

    assert func(1, 2, a=1, b=2) == expected
    assert func(1, 2, b=2, a=1) == expected


def test_get_arg_by_name_varargs_expanded_exclude_search_error():
    # Ensure that the name of the variable positional arguments is not included
    # in the search, when expand_varargs is True.

    @return_map(names=["args"], expand_varargs=True)
    def func(*args, **kwargs):
        pass

    with pytest.raises(ValueError):
        func(1, 2, a=1, b=2)


def test_get_arg_by_name_non_existent_error():
    # Ensure that an error is raised when trying to get an argument by name
    # that does not exist in the function's signature.

    @return_map(names=["c"])
    def func(a, b):
        pass

    with pytest.raises(ValueError):
        func(1, 2)


def test_get_arg_by_name_varargs_expanded_non_existent_error():
    # Ensure that an error is raised when trying to get an argument by name
    # that does not exist in the function's signature.

    @return_map(names=["c"], expand_varargs=True)
    def func(*args, **kwargs):
        pass

    with pytest.raises(ValueError):
        func(1, 2, a=1, b=2)


def test_get_arg_by_name_complex_1():
    @return_map(
        names=[
            "pos_only_wo_def",
            "pos_or_kw_wo_def",
            "pos_or_kw_w_def",
            "args",
            "kw_only_wo_def",
            "kw_only_w_def",
            "kwargs",
        ]
    )
    def func(
        pos_only_wo_def,
        /,
        pos_or_kw_wo_def,
        pos_or_kw_w_def=3,
        *args,
        kw_only_wo_def,
        kw_only_w_def=6,
        **kwargs,
    ):
        pass

    expected = {
        "pos_only_wo_def": 1,
        "pos_or_kw_wo_def": 2,
        "pos_or_kw_w_def": 3,
        "args": (4, 4.5),
        "kw_only_wo_def": 5,
        "kw_only_w_def": 6,
        "kwargs": {"undef_kw_1": 7, "unef_kw_2": 8},
    }

    assert (
        func(
            1,
            2,
            3,
            4,
            4.5,
            kw_only_wo_def=5,
            kw_only_w_def=6,
            undef_kw_1=7,
            unef_kw_2=8,
        )
        == expected
    )

    assert (
        func(
            1,
            2,
            3,
            4,
            4.5,
            kw_only_wo_def=5,
            undef_kw_1=7,
            unef_kw_2=8,
        )
        == expected
    )


def test_get_arg_by_name_complex_2():
    @return_map(
        names=[
            "pos_only_wo_def",
            "pos_only_w_def",
            "pos_or_kw_w_def",
            "args",
            "kw_only_wo_def",
            "kw_only_w_def",
            "kwargs",
        ]
    )
    def func(
        pos_only_wo_def,  # Positional-only argument without default
        pos_only_w_def=2,
        /,  # Positional-only argument with default
        pos_or_kw_w_def=3,  # Positional-or-keyword argument with default
        *args,  # Variable positional arguments
        kw_only_wo_def,  # Keyword-only argument without default
        kw_only_w_def=6,  # Keyword-only arguments
        **kwargs,  # Variable keyword arguments
    ):
        pass

    expected = {
        "pos_only_wo_def": 1,
        "pos_only_w_def": 2,
        "pos_or_kw_w_def": 3,
        "args": (4, 4.5),
        "kw_only_wo_def": 5,
        "kw_only_w_def": 6,
        "kwargs": {"undef_kw_1": 7, "unef_kw_2": 8},
    }

    assert (
        func(
            1,
            2,
            3,
            4,
            4.5,
            kw_only_wo_def=5,
            kw_only_w_def=6,
            undef_kw_1=7,
            unef_kw_2=8,
        )
        == expected
    )
