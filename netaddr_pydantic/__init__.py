"""This module allows :py:mod:`netaddr` objects to be used as field types
annotations in pydantic models.

"""

from typing import Any, Annotated


import netaddr
from netaddr.core import AddrFormatError

from pydantic import PlainSerializer, PlainValidator, Tag, Discriminator
from pydantic_core import PydanticCustomError


__version__ = "0.1.1"


IPAddress = Annotated[
    netaddr.IPAddress, PlainValidator(netaddr.IPAddress), PlainSerializer(str)
]

IPNetwork = Annotated[
    netaddr.IPNetwork, PlainValidator(netaddr.IPNetwork), PlainSerializer(str)
]

IPGlob = Annotated[
    netaddr.IPGlob, PlainValidator(netaddr.IPGlob), PlainSerializer(str)
]


def iprange_validator(value: Any) -> netaddr.IPRange:
    """Allow strings and some kinds of tuple/list to be used as IPRange"""
    if isinstance(value, (tuple, list)) and len(value) == 2:
        return netaddr.IPRange(*value)
    if isinstance(value, str):
        try:
            start, end = value.split("-", maxsplit=1)
            return netaddr.IPRange(start, end)
        except (TypeError, ValueError, AddrFormatError):
            pass
    raise ValueError(value)


IPRange = Annotated[
    netaddr.IPRange, PlainValidator(iprange_validator), PlainSerializer(str)
]


def ipset_validator(value: Any) -> netaddr.IPSet:
    """Data validation for IPSet"""
    if isinstance(value, (tuple, list, set)):
        return netaddr.IPSet(value)
    raise ValueError(value)


def ipset_serializer(ipset: netaddr.IPSet) -> list[str]:
    """IPSet Serialization as list of strings"""
    return [str(cidr) for cidr in ipset.iter_cidrs()]


IPSet = Annotated[
    netaddr.IPSet,
    PlainValidator(ipset_validator, json_schema_input_type=list[str | int]),
    PlainSerializer(ipset_serializer, return_type=list[str]),
]


def ipany_discriminator(value: Any) -> str:
    """Attempt to detect most adapted class from input value"""
    if isinstance(value, (list, tuple, set)):
        return "set"
    if not isinstance(value, str):
        raise PydanticCustomError(
            "netaddr_pydantic_error",
            "unexpected type {value_type} for netaddr conversion",
            {"value_type": type(value), "value": value},
        )
    if "/" in value:
        return "network"
    if "-" in value:
        return "range"
    if "*" in value:
        return "glob"
    return "address"


IPAny = Annotated[
    Annotated[IPAddress, Tag("address")]
    | Annotated[IPNetwork, Tag("network")]
    | Annotated[IPRange, Tag("range")]
    | Annotated[IPGlob, Tag("glob")]
    | Annotated[IPSet, Tag("set")],
    Discriminator(ipany_discriminator),
]

__all__ = ("IPAddress", "IPNetwork", "IPGlob", "IPRange", "IPSet", "IPAny")
