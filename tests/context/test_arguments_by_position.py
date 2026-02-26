import pytest

from argbox import Context


def return_map(positions: list[int], expand_varargs: bool = False):
    def wrapper(func):
        def wrapped(*args, **kwargs):
            ctx = Context(func, args, kwargs, expand_varargs)
            mapping = {str(pos): ctx.get_arg(position=pos) for pos in positions}
            return mapping

        return wrapped

    return wrapper


def test_get_arg_by_position_positional_or_keyword():
    @return_map(positions=[0, 1])
    def func(a, b):
        pass

    expected = {"0": 1, "1": 2}

    assert func(1, 2) == expected
    assert func(a=1, b=2) == expected
    assert func(1, b=2) == expected
    assert func(b=2, a=1) == expected
    assert func(*[1, 2]) == expected
    assert func(**{"a": 1, "b": 2}) == expected


def test_get_arg_by_position_positional_or_keyword_with_defaults():
    @return_map(positions=[0, 1])
    def func(a=1, b=2):
        pass

    expected = {"0": 1, "1": 2}

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


def test_get_arg_by_position_positional_only():
    @return_map(positions=[0, 1])
    def func(a, b, /):
        pass

    expected = {"0": 1, "1": 2}

    assert func(1, 2) == expected
    assert func(*[1, 2]) == expected


def test_get_arg_by_position_positional_only_with_defaults():
    @return_map(positions=[0, 1])
    def func(a=1, b=2, /):
        pass

    expected = {"0": 1, "1": 2}

    assert func() == expected
    assert func(1) == expected
    assert func(1, 2) == expected
    assert func(*[1, 2]) == expected


def test_get_arg_by_position_keyword_only():
    @return_map(positions=[0, 1])
    def func(*, a, b):
        pass

    expected = {"0": 1, "1": 2}

    assert func(a=1, b=2) == expected
    assert func(b=2, a=1) == expected
    assert func(**{"a": 1, "b": 2}) == expected
    assert func(**{"b": 2, "a": 1}) == expected


def test_get_arg_by_position_keyword_only_with_defaults():
    @return_map(positions=[0, 1])
    def func(*, a=1, b=2):
        pass

    expected = {"0": 1, "1": 2}

    assert func() == expected
    assert func(a=1) == expected
    assert func(b=2) == expected
    assert func(a=1, b=2) == expected
    assert func(b=2, a=1) == expected
    assert func(**{"a": 1, "b": 2}) == expected
    assert func(**{"b": 2, "a": 1}) == expected


def test_get_arg_by_position_varargs():
    @return_map(positions=[0, 1])
    def func(*args, **kwargs):
        pass

    expected = {"0": (1, 2), "1": {"a": 1, "b": 2}}

    assert func(1, 2, a=1, b=2) == expected
    assert func(1, 2, b=2, a=1) == expected
    assert func(*[1, 2], **{"a": 1, "b": 2}) == expected
    assert func(*[1, 2], **{"b": 2, "a": 1}) == expected


def test_get_arg_by_position_varargs_expanded():
    @return_map(positions=[0, 1, 2, 3], expand_varargs=True)
    def func(*args, **kwargs):
        pass

    expected = {"0": 1, "1": 2, "2": 3, "3": 4}

    assert func(1, 2, a=3, b=4) == expected
    assert func(1, 2, b=3, a=4) == expected


def test_get_arg_by_position_non_existent_error():
    @return_map(positions=[2])
    def func(a, b):
        pass

    with pytest.raises(ValueError):
        func(1, 2)


def test_get_arg_by_position_varargs_expanded_non_existent_error():
    @return_map(positions=[4], expand_varargs=True)
    def func(*args, **kwargs):
        pass

    with pytest.raises(ValueError):
        func(1, 2, a=1, b=2)


def test_get_arg_by_position_complex_1():
    @return_map(positions=[0, 1, 2, 3, 4, 5, 6])
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
        "0": 1,
        "1": 2,
        "2": 3,
        "3": (4, 4.5),
        "4": 5,
        "5": 6,
        "6": {"undef_kw_1": 7, "unef_kw_2": 8},
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


def test_get_arg_by_position_complex_2():
    @return_map(positions=[0, 1, 2, 3, 4, 5, 6])
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
        "0": 1,
        "1": 2,
        "2": 3,
        "3": (4, 4.5),
        "4": 5,
        "5": 6,
        "6": {"undef_kw_1": 7, "unef_kw_2": 8},
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
