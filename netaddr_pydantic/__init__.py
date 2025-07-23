"""This module allows :py:mod:`netaddr` objects to be used as field types
annotations in pydantic models.

"""

from typing import Annotated

import netaddr
from pydantic import PlainSerializer, PlainValidator, Tag, Discriminator

from .friends import (
    ipv,
    iprange_validator,
    ipset_validator,
    ipset_serializer,
    ipany_discriminator,
)

__version__ = "0.2.0"


IPAddress = Annotated[
    netaddr.IPAddress, PlainValidator(netaddr.IPAddress), PlainSerializer(str)
]

IPv4Address = Annotated[
    netaddr.IPAddress, ipv(4, netaddr.IPAddress), PlainSerializer(str)
]

IPv6Address = Annotated[
    netaddr.IPAddress, ipv(6, netaddr.IPAddress), PlainSerializer(str)
]

IPNetwork = Annotated[
    netaddr.IPNetwork, PlainValidator(netaddr.IPNetwork), PlainSerializer(str)
]

IPv4Network = Annotated[
    netaddr.IPNetwork, ipv(4, netaddr.IPNetwork), PlainSerializer(str)
]

IPv6Network = Annotated[
    netaddr.IPNetwork, ipv(6, netaddr.IPNetwork), PlainSerializer(str)
]


IPGlob = Annotated[
    netaddr.IPGlob, PlainValidator(netaddr.IPGlob), PlainSerializer(str)
]

IPRange = Annotated[
    netaddr.IPRange, PlainValidator(iprange_validator), PlainSerializer(str)
]


IPSet = Annotated[
    netaddr.IPSet,
    PlainValidator(ipset_validator, json_schema_input_type=list[str | int]),
    PlainSerializer(ipset_serializer, return_type=list[str]),
]


IPAny = Annotated[
    Annotated[IPAddress, Tag("address")]
    | Annotated[IPNetwork, Tag("network")]
    | Annotated[IPRange, Tag("range")]
    | Annotated[IPGlob, Tag("glob")]
    | Annotated[IPSet, Tag("set")],
    Discriminator(ipany_discriminator),
]

__all__ = (
    "IPAddress",
    "IPv4Address",
    "IPv6Address",
    "IPNetwork",
    "IPv4Network",
    "IPv6Network",
    "IPGlob",
    "IPRange",
    "IPSet",
    "IPAny",
)
