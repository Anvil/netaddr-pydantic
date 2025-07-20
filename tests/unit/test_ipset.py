"""Unit tests for netaddr_pydantic.IPRange"""

import random
from typing import TypeAlias, cast
from collections.abc import Callable

import pytest
import netaddr
import pydantic

from netaddr_pydantic import IPSet

from .conftest import GenericModel, CreateAddressFixture, CreateNetworkFixture


def test_ipset(
    create_address: CreateAddressFixture, create_network: CreateNetworkFixture
) -> None:
    """Test input values validations"""
    Model: TypeAlias = GenericModel[IPSet]
    functions = cast(
        list[Callable[[], netaddr.IPAddress | netaddr.IPNetwork | str | int]],
        [
            create_network,
            create_address,
            lambda: str(create_address()),
            lambda: int(create_address()),
            lambda: str(create_network()),
        ],
    )
    value = [
        *[function() for function in functions],
        *[
            function()
            for function in random.choices(functions, k=random.randint(10, 20))
        ],
    ]
    ipset = netaddr.IPSet(value)

    m = Model(field=value)

    assert isinstance(m.field, netaddr.IPSet)
    assert m.field == ipset
    assert Model(**m.model_dump()) == m


def test_bad_ipset() -> None:
    """Failure tests of the IPSet validator"""
    Model: TypeAlias = GenericModel[IPSet]
    with pytest.raises(pydantic.ValidationError):
        Model(field=1)
