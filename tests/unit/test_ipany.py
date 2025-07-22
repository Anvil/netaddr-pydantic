"""Unit tests for netaddr_pydantic.IPAny and other IPvXAddress/Network"""

from contextlib import nullcontext as does_not_raise, AbstractContextManager
from typing import TypeAlias, Any

import netaddr
import pytest
from pydantic_core import PydanticCustomError
from pydantic import ValidationError

from netaddr_pydantic import (
    IPAny,
    IPv4Address,
    IPv6Address,
    IPv4Network,
    IPv6Network,
)

from .conftest import GenericModel, InetFixture


@pytest.mark.parametrize(
    "value, cls_",
    [
        ("192.168.1.1", netaddr.IPAddress),
        ("192.168.1.0/24", netaddr.IPNetwork),
        ("192.168.1.1-192.168.1.3", netaddr.IPRange),
        ("192.168.1.*", netaddr.IPGlob),
        (["192.168.1.1", "192.168.1.2"], netaddr.IPSet),
    ],
)
def test_ipany(value: str, cls_: type[Any]) -> None:
    """Test input values validations"""
    Model: TypeAlias = GenericModel[IPAny]
    print(value, cls_)
    m = Model(field=value)

    assert isinstance(m.field, cls_)


def test_bad_ipany() -> None:
    """Discrimination failure unit test"""
    Model: TypeAlias = GenericModel[IPAny]
    with pytest.raises(PydanticCustomError):
        Model(field=1)


@pytest.mark.parametrize("address", ("1.2.3.0", "dead:beef::1"))
@pytest.mark.parametrize("netaddr_t", (netaddr.IPNetwork, netaddr.IPAddress))
def test_ipv46xxx(
    inet: InetFixture,
    address: str,
    netaddr_t: type[netaddr.IPNetwork | netaddr.IPAddress],
) -> None:
    """Validate that IPv4Address/IPv4Network fields validate actual IPv4
    addresses and refuses IPv6 addresses. And vice versa.
    And vice-versa....
    """
    model_type: type[GenericModel[Any]]
    match (inet, netaddr_t):
        case (4, netaddr.IPNetwork):
            model_type = GenericModel[IPv4Network]
        case (6, netaddr.IPNetwork):
            model_type = GenericModel[IPv6Network]
        case (4, netaddr.IPAddress):
            model_type = GenericModel[IPv4Address]
        case (6, netaddr.IPAddress):
            model_type = GenericModel[IPv6Address]

    if netaddr_t == netaddr.IPNetwork:
        address += "/24"

    expectation: AbstractContextManager[Any]
    if inet == netaddr_t(address).version:
        expectation = does_not_raise()
    else:
        expectation = pytest.raises(ValidationError)

    with expectation:
        model_type(field=address)
