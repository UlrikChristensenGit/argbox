import pytest

import argbox

INFINITY = object()


@argbox.dispatch_on_rule
def divide_positional(numerator, denominator):
    ...


@divide_positional.register(lambda x: True, lambda y: y != 0)
def _(numerator, denominator):
    return numerator / denominator


@divide_positional.register(lambda x: x != 0, lambda y: y == 0)
def _(numerator, denominator):
    return INFINITY


@argbox.dispatch_on_rule
def divide_keyword(numerator, denominator):
    ...


@divide_keyword.register(denominator=lambda y: y != 0, numerator=lambda x: True)
def _(numerator, denominator):
    return numerator / denominator


@divide_keyword.register(denominator=lambda y: y == 0, numerator=lambda x: x != 0)
def _(numerator, denominator):
    return INFINITY


@pytest.mark.parametrize("divide", [divide_positional, divide_keyword])
def test_dispatch_on_rule(divide):
    assert divide(10, 2) == 5.0
    assert divide(10, 0) is INFINITY
    assert divide(10, denominator=0) is INFINITY
    assert divide(numerator=10, denominator=0) is INFINITY
    assert divide(denominator=0, numerator=10) is INFINITY

    with pytest.raises(NotImplementedError):
        divide(0, 0)

    with pytest.raises(NotImplementedError):
        divide(denominator=0, numerator=0)


@argbox.dispatch_on_rule
def divide_var_positional(*args):
    ...


@divide_var_positional.register(lambda x: True, lambda y: y != 0)
def _(*args):
    return args[0] / args[1]


@divide_var_positional.register(lambda x: x != 0, lambda y: y == 0)
def _(*args):
    return INFINITY


def test_dispatch_on_rule_var_positional():
    assert divide_var_positional(10, 2) == 5.0
    assert divide_var_positional(10, 0) is INFINITY

    with pytest.raises(NotImplementedError):
        divide_var_positional(0, 0)


@argbox.dispatch_on_rule
def divide_var_keyword(**kwargs):
    ...


@divide_var_keyword.register(denominator=lambda y: y != 0, numerator=lambda x: True)
def _(**kwargs):
    return kwargs["numerator"] / kwargs["denominator"]


@divide_var_keyword.register(denominator=lambda y: y == 0, numerator=lambda x: x != 0)
def _(**kwargs):
    return INFINITY


def test_dispatch_on_rule_var_keyword():
    assert divide_var_keyword(numerator=10, denominator=2) == 5.0
    assert divide_var_keyword(numerator=10, denominator=0) is INFINITY

    with pytest.raises(NotImplementedError):
        divide_var_keyword(numerator=0, denominator=0)
