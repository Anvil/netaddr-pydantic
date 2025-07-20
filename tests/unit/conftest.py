"""Fixtures and unit tests common code"""

from typing import Literal, Generic, TypeVar, cast, Protocol

from collections.abc import Callable
import random

import netaddr
import pytest
from pydantic import BaseModel

# pylint: disable=redefined-outer-name

InetFixture = Literal[4, 6]


@pytest.fixture(params=[4, 6])
def inet(request: pytest.FixtureRequest) -> InetFixture:
    """The Internet protocol version we're deadling with"""
    return cast(InetFixture, request.param)


MaxLengthFixture = Literal[32, 128]


@pytest.fixture
def max_len(inet: InetFixture) -> MaxLengthFixture:
    """The maximum prefix length for internet protocol version"""
    lengths: dict[InetFixture, MaxLengthFixture] = {4: 32, 6: 128}
    return lengths[inet]


@pytest.fixture
def limit(max_len: MaxLengthFixture) -> int:
    """The maximum address value in given Internet Protocol version"""
    return cast(int, 2**max_len)


FieldT = TypeVar("FieldT")


class GenericModel(BaseModel, Generic[FieldT]):
    """Another stupid model. This is a défilé."""

    field: FieldT


class CreateAddressFixture(Protocol):
    """Type returned by the :py:func:`create_address` fixxture."""

    # pylint: disable=too-few-public-methods
    def __call__(self, minimum: int = ..., /) -> netaddr.IPAddress: ...


@pytest.fixture
def create_address(inet: InetFixture, limit: int) -> CreateAddressFixture:
    """Provides a random :py:class:`netaddr.IPAddress` generation function for
    current Internet Protocol version.
    """

    def gen_address(minimum: int = 1) -> netaddr.IPAddress:
        return netaddr.IPAddress(
            random.randint(minimum, limit - 1), version=inet
        )

    return gen_address


CreateNetworkFixture = Callable[[], netaddr.IPNetwork]


@pytest.fixture
def create_network(
    inet: InetFixture,
    max_len: MaxLengthFixture,
    create_address: CreateAddressFixture,
) -> CreateNetworkFixture:
    """Provides a random :py:class:`netaddr.IPNetwork` generation function for
    current Internet Protocol version.
    """

    def gen_network() -> netaddr.IPNetwork:

        return netaddr.IPNetwork(
            (cast(int, create_address().value), random.randint(1, max_len)),
            version=inet,
        )

    return gen_network
