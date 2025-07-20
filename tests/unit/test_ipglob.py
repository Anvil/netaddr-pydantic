"""Unit tests for netaddr_pydantic.IPAddress"""

from typing import TypeAlias

import netaddr

from netaddr_pydantic import IPGlob

from .conftest import GenericModel


def test_ipglob() -> None:
    """Test input values validations"""
    Model: TypeAlias = GenericModel[IPGlob]
    value, size = "192.168.1.*", 256
    glob = netaddr.IPGlob(value)

    m = Model(field=value)

    assert isinstance(m.field, netaddr.IPGlob)
    assert m.field.size == size
    assert m.field == glob
    assert m.model_dump()["field"] == value
    assert m.model_dump_json() == f'{{"field":"{glob}"}}'
    assert Model.model_validate_json(m.model_dump_json()) == m
