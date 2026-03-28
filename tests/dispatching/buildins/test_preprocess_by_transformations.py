import pytest

import argbox


@argbox.preprocess_by_transformations(
    lambda s: str(s),
    lambda n: int(n),
)
def substring_positional(string, number):
    return string[:number]


@argbox.preprocess_by_transformations(
    number=lambda n: int(n),
    string=lambda s: str(s),
)
def substring_keyword(string, number):
    return string[:number]


@pytest.mark.parametrize("substring", [substring_positional, substring_keyword])
def test_preprocess_by_transformations(substring):
    assert substring("Hello, World!", "5") == "Hello"
    assert substring("Hello world!", number=5) == "Hello"
    assert substring(string="Hello, World!", number="5") == "Hello"
    assert substring(number="5", string="Hello, World!") == "Hello"

    with pytest.raises(ValueError):
        substring("Hello, World!", "five")

    with pytest.raises(ValueError):
        substring("Hello, World!", number="five")

    with pytest.raises(ValueError):
        substring(string="Hello, World!", number="five")

    with pytest.raises(ValueError):
        substring(number="five", string="Hello, World!")


@argbox.preprocess_by_transformations(
    lambda s: str(s),
    lambda n: int(n),
)
def substring_var_args(*args):
    return args[0][: args[1]]


def test_preprocess_by_transformations_var_args():
    assert substring_var_args("Hello, World!", "5") == "Hello"

    with pytest.raises(ValueError):
        substring_var_args("Hello, World!", "five")


@argbox.preprocess_by_transformations(
    number=lambda n: int(n),
    string=lambda s: str(s),
)
def substring_var_kwargs(**kwargs):
    return kwargs["string"][: kwargs["number"]]


def test_preprocess_by_transformations_var_kwargs():
    assert substring_var_kwargs(string="Hello, World!", number="5") == "Hello"

    with pytest.raises(ValueError):
        substring_var_kwargs(string="Hello, World!", number="five")
