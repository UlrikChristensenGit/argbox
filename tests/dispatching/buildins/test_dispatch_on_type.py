import pytest

import argbox


@argbox.dispatch_on_type
def scale_positional(scalar, vector):
    ...


@scale_positional.register(float, float)
def _(scalar, vector):
    return scalar * vector


@scale_positional.register(float, list)
def _(scalar, vector):
    return [scalar * comp for comp in vector]


@argbox.dispatch_on_type
def scale_keyword(scalar, vector):
    ...


@scale_keyword.register(vector=float, scalar=float)
def _(scalar, vector):
    return scalar * vector


@scale_keyword.register(vector=list, scalar=float)
def _(scalar, vector):
    return [scalar * comp for comp in vector]


@pytest.mark.parametrize("scale", [scale_positional, scale_keyword])
def test_dispatch_on_type(scale):
    assert scale(2.0, 3.0) == 6.0
    assert scale(2.0, [1.0, 2.0]) == [2.0, 4.0]
    assert scale(2.0, vector=[1.0, 2.0]) == [2.0, 4.0]
    assert scale(scalar=2.0, vector=[1.0, 2.0]) == [2.0, 4.0]
    assert scale(vector=[1.0, 2.0], scalar=2.0) == [2.0, 4.0]

    with pytest.raises(NotImplementedError):
        scale([1.0, 2.0], 2.0)

    with pytest.raises(NotImplementedError):
        scale(vector=2.0, scalar=[1.0, 2.0])


@argbox.dispatch_on_type
def scale_var_positional(*args):
    ...


@scale_var_positional.register(float, float)
def _(*args):
    return args[0] * args[1]


@scale_var_positional.register(float, list)
def _(*args):
    return [args[0] * comp for comp in args[1]]


def test_dispatch_on_type_var_args():
    assert scale_var_positional(2.0, 3.0) == 6.0
    assert scale_var_positional(2.0, [1.0, 2.0]) == [2.0, 4.0]

    with pytest.raises(NotImplementedError):
        scale_var_positional([1.0, 2.0], 2.0)


@argbox.dispatch_on_type
def scale_var_keyword(**kwargs):
    ...


@scale_var_keyword.register(scalar=float, vector=float)
def _(**kwargs):
    return kwargs["scalar"] * kwargs["vector"]


@scale_var_keyword.register(scalar=float, vector=list)
def _(**kwargs):
    return [kwargs["scalar"] * comp for comp in kwargs["vector"]]


def test_dispatch_on_type_var_kwargs():
    assert scale_var_keyword(scalar=2.0, vector=3.0) == 6.0
    assert scale_var_keyword(scalar=2.0, vector=[1.0, 2.0]) == [2.0, 4.0]

    with pytest.raises(NotImplementedError):
        scale_var_keyword(scalar=[1.0, 2.0], vector=2.0)
