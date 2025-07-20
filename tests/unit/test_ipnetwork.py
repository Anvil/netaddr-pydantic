"""Unit tests for netaddr_pydantic.IPNetwork"""

from typing import Any, TypeAlias
from collections.abc import Callable

import netaddr
import pytest

from netaddr_pydantic import IPNetwork

from .conftest import GenericModel, CreateNetworkFixture


@pytest.mark.parametrize(
    "func",
    (str, lambda x: x, lambda net: (net.value, net.prefixlen)),
    ids=("str", "IPNetwork", "tuple[int, int]"),
)
def test_ipnetwork(
    func: Callable[[netaddr.IPNetwork], Any],
    create_network: CreateNetworkFixture,
) -> None:
    """Test input values validations"""
    Model: TypeAlias = GenericModel[IPNetwork]
    network = create_network()
    value = func(network)

    m = Model(field=value)

    assert isinstance(m.field, netaddr.IPNetwork)
    assert m.field == network
    assert m.model_dump()["field"] == str(network)
