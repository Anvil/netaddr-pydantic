# netaddr-pydantic

[![PyPI version](https://img.shields.io/pypi/v/netaddr-pydantic?logo=pypi&style=plastic)](https://pypi.python.org/pypi/netaddr-pydantic/)
[![Supported Python Version](https://img.shields.io/pypi/pyversions/netaddr-pydantic?logo=python&style=plastic)](https://pypi.python.org/pypi/netaddr-pydantic/)
[![License](https://img.shields.io/pypi/l/netaddr-pydantic?color=green&logo=GNU&style=plastic)](https://github.com/Anvil/netaddr-pydantic/blob/main/LICENSE)

[![Pylint Static Quality Github Action](https://github.com/Anvil/netaddr-pydantic/actions/workflows/pylint.yml/badge.svg)](https://github.com/Anvil/netaddr-pydantic/actions/workflows/pylint.yml)
[![Mypy Static Quality Github Action](https://github.com/Anvil/netaddr-pydantic/actions/workflows/mypy.yml/badge.svg)](https://github.com/Anvil/netaddr-pydantic/actions/workflows/mypy.yml)
[![Pylint Static Quality Github Action](https://github.com/Anvil/netaddr-pydantic/actions/workflows/python-app.yml/badge.svg)](https://github.com/Anvil/netaddr-pydantic/actions/workflows/python-app.yml)

Use [Netaddr](https://pypi.org/project/netaddr/) objects in [Pydantic](https://docs.pydantic.dev/latest/) Models


## Rational

### Origin of the issue.

The [ipaddress](https://docs.python.org/3/library/ipaddress.html) module supports Iternet Protocol addresses and networks but lacks support for funny objects such as ranges, IP sets, globbing and so on.

The `Pydantic` framework provides out-of-the-box support for IPv4/IPv6 addresses and networks through the `ipaddress` module and this allows you to easily validate or serialize data from/to interfaces.

```python
import pydantic

class Model(pydantic.BaseModel):
    address: pydantic.IPvAnyAddress


m = Model(address="1.2.3.4")
print(type(m.address))
print(m.model_dump_json())
```

This produces:

```
<class 'ipaddress.IPv4Address'>
{"address":"1.2.3.4"}
```


Unfortunately, once the data is parsed, `ipaddress` objects cannot be inserted as-is to a `netaddr.IPSet` for example.

Alternatively, you would want to switch to `netaddr`-typed fields with like this:


```python
import pydantic
import netaddr

class Model(pydantic.BaseModel):
    address: netaddr.IPAddress
```

Unfortunately, `pydantic` cannot compile such thing:

```
pydantic.errors.PydanticSchemaGenerationError: Unable to generate pydantic-core schema for <class 'netaddr.ip.IPAddress'>. Set `arbitrary_types_allowed=True` in the model_config to ignore this error or implement `__get_pydantic_core_schema__` on your type to fully support it.

If you got this error by calling handler(<some type>) within `__get_pydantic_core_schema__` then you likely need to call `handler.generate_schema(<some type>)` since we do not call `__get_pydantic_core_schema__` on `<some type>` otherwise to avoid infinite recursion.

For further information visit https://errors.pydantic.dev/2.11/u/schema-for-unknown-type
```

This is due to the lack of `pydantic` metadata in `netaddr` classes. Mainly, `pydantic` needs to know how to validate (from basic types, such as strings and integers) and how to to serialize the objects (return the basic types).


### Should you use netaddr-pydantic?


A way to fix this issue is to write your own validators and serializers and if you're lazy enough (no judgement here :]), this is just what `netaddr-pydantic` is bringing on the table.

This code:

```python
import pydantic
import netaddr_pydantic

class Model(pydantic.BaseModel):
    address: netaddr_pydantic.IPAddress

m = Model(address="1.2.3.4")
print(type(m.address))
print(m.model_dump_json())
```

Naturally produces the following:

```
<class 'netaddr.ip.IPAddress'>
{"address":"1.2.3.4"}
```

Basically, `netaddr-pydantic` just defines `Annotated` types with `pydantic` functional validators and serializers. For instance, `IPAddress` and `IPNetwork` are just defined this way:

```python
from typing import Annotated
from pydantic import PlainValidator, PlainSerializer
import netaddr

IPAddress = Annotated[
    netaddr.IPAddress, PlainValidator(netaddr.IPAddress), PlainSerializer(str)
]

IPNetwork = Annotated[
    netaddr.IPNetwork, PlainValidator(netaddr.IPNetwork), PlainSerializer(str)
]
```

And by all means, if *this* is all you need, do not bother with `netaddr-pydantic`. But if you need to use `IPRange`s and/or `IPSet`s as well then maybe you should use `netaddr-pydantic`, because, while `IPrange` and `IPSet` validators and serializers are just a very little bit more complex, I dont feel they are worth repeating.

Plus this is what *I* need in my own production environment, these days, so it will be maintained for a while.

## Still there? OK, then let's see.

The `netaddr-pydantic` annotations are only really useful in a `pydantic` context. You can use plain `netaddr` in other places.

### Supported objects and conversions


| Object Types | Can be obtained from | Serialized as | Comment |
| :----------- | :------------------: | :-----------: | :------ |
| IPAddress    | `str`, `int` | `str` |  | 
| IPNetwork    | `str`, 2-items `tuple` or `list` | a CIDR `str` | |
| IPRange      | `"<start-ip>-<end-ip>"` `str` or 2-items `list` or `tuple` | a `"<start-ip>-<end-ip>"` `str` | 
| IPSet        | `list`, `tuple` or `set` of `str`s or `int`s | `list` of `str`s. The `IPSet.iter_cidrs` is used to compute the items of the list. | If you do not want to work with `IPSet`, use `list[IPAddress \| IPNetwork]`, or similar. |
| IPGlob | `str` | `str` | `netaddr` implementation seems to be limited to IPv4 


The validation relies mostly on `netaddr` objects constructors. There's currently no bijection possible from the validated format to the serialized format. I do not intend to implement it at this time.

### Additionnal features

That may not be much, but an `IPAny` type is available. `pydantic` should produce the most acccurate object depending of the source object. An `IPAny` field will produce

* an `IPSet` if provided type is `list`, `tuple` or `set` 
* an `IPNetwork` if value is a CIDR `str`
* an `IPRange` if value is an `str` containing a `-` character
* an `IPGlob` if value is an `str` containing a `*` char.
* an `IPAddress` in other cases.
