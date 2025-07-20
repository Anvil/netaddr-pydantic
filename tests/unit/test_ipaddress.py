"""Unit tests for netaddr_pydantic.IPAddress"""

from typing import Any, TypeAlias
from collections.abc import Callable

import netaddr
import pytest

from netaddr_pydantic import IPAddress

from .conftest import InetFixture, GenericModel, CreateAddressFixture


@pytest.mark.parametrize(
    "func", (str, int, lambda x: x), ids=("str", "int", "IPAddress")
)
def test_ipaddress(
    func: Callable[[netaddr.IPAddress], Any],
    inet: InetFixture,
    create_address: CreateAddressFixture,
) -> None:
    """Test input values validations"""
    Model: TypeAlias = GenericModel[IPAddress]
    address = create_address()
    value = func(address)

    m = Model(field=value)

    assert isinstance(m.field, netaddr.IPAddress)
    assert m.field == address
    assert m.field.version == inet
    assert m.model_dump()["field"] == str(address)
    assert m.model_dump_json() == f'{{"field":"{address}"}}'
    assert Model.model_validate_json(m.model_dump_json()) == m
