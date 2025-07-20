"""Unit tests for netaddr_pydantic.IPRange"""

from typing import TypeAlias, cast, Any
from collections.abc import Callable

import netaddr
import pytest
import pydantic

from netaddr_pydantic import IPRange

from .conftest import GenericModel, CreateAddressFixture


@pytest.mark.parametrize(
    "func",
    (str, lambda iprange: (iprange.first, iprange.last)),
    ids=("str", "tuple[int, int]"),
)
def test_iprange(
    func: Callable[[netaddr.IPRange], IPRange],
    create_address: CreateAddressFixture,
) -> None:
    """Test input values validations"""
    Model: TypeAlias = GenericModel[IPRange]
    start = create_address()
    end = create_address(cast(int, start.value))
    iprange = netaddr.IPRange(start, end)
    value = func(iprange)

    m = Model(field=value)

    assert isinstance(m.field, netaddr.IPRange)
    assert m.field == iprange
    assert m.model_dump()["field"] == str(iprange)


@pytest.mark.parametrize(
    "value", ["1", (), [], 1], ids=("invalid string", "()", "[]", "int")
)
def test_bad_iprange(value: Any) -> None:
    """Test failures in IPRange custom validator"""
    Model: TypeAlias = GenericModel[IPRange]
    with pytest.raises(pydantic.ValidationError):
        Model(field=value)
