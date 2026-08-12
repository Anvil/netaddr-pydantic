"""Test plain Unions of Netaddr types"""

from itertools import permutations
from typing import Union, Any

from pydantic import TypeAdapter
import pytest

from netaddr_pydantic import IPAddress, IPRange, IPNetwork


def union_ids(types: list[type[Any]]) -> str:
    """Produce a nice id string from some soon-to-be-unioned types"""
    return "|".join(str(type_.__args__[0].__name__) for type_ in types)


@pytest.mark.parametrize(
    "types",
    tuple(permutations((IPAddress, IPRange, IPNetwork))),
    ids=union_ids,
)
@pytest.mark.parametrize(
    "input_value", ("1.2.3.4", "1.2.3.0/24", "1.2.3.4-1.2.3.5")
)
def test_union(types: list[type[Any]], input_value: str) -> None:
    """Validate that unions of IPAddress, IPRange, IPNetwork can actually
    produce valid objects, whatever the order.
    """
    union = Union[*types]  # type: ignore[valid-type]
    adapter: TypeAdapter[union] = TypeAdapter(union)

    assert adapter.validate_python(input_value)
