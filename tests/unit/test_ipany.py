"""Unit tests for netaddr_pydantic.IPAny"""

from typing import TypeAlias, Any

import netaddr
import pytest
from pydantic_core import PydanticCustomError

from netaddr_pydantic import IPAny

from .conftest import GenericModel


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
