"""Friends are better than helpers. Deal with it.

Functional validators, serializers, discriminators, etc. are all here.

"""

from typing import Any, TypeVar, Literal
from collections.abc import Callable

import netaddr
from pydantic_core import PydanticCustomError
from pydantic import PlainValidator


ReturnT = TypeVar("ReturnT")


def ipv(
    version: Literal[4, 6], func: Callable[..., ReturnT]
) -> PlainValidator:
    """Decorate to automatically insert the named ``version`` parameter
    function to given specific value in function calls. And also to correctly
    raise a ValueError to correctly trigger native pydantic error handling.

    Then build :py:class:`pydantic.PlainValidator` with it and return that.
    """

    def _validator(value: Any) -> ReturnT:
        try:
            return func(value, version=version)
        except netaddr.AddrFormatError as error:
            raise ValueError(str(error)) from error

    return PlainValidator(_validator)


def iprange_validator(value: Any) -> netaddr.IPRange:
    """Allow strings and some kinds of tuple/list to be used as IPRange"""
    if isinstance(value, (tuple, list)) and len(value) == 2:
        return netaddr.IPRange(*value)
    if isinstance(value, str):
        try:
            start, end = value.split("-", maxsplit=1)
            return netaddr.IPRange(start, end)
        except (TypeError, ValueError, netaddr.AddrFormatError):
            pass
    raise ValueError(value)


def ipset_validator(value: Any) -> netaddr.IPSet:
    """Data validation for IPSet"""
    if isinstance(value, (tuple, list, set)):
        return netaddr.IPSet(value)
    raise ValueError(value)


def ipset_serializer(ipset: netaddr.IPSet) -> list[str]:
    """IPSet Serialization as list of strings"""
    return [str(cidr) for cidr in ipset.iter_cidrs()]


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
