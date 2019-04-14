"""Attributes for Nodes and Edges"""
from functools import partialmethod
from typing import (
    Any,
    Callable,
    Iterable,
    NamedTuple,
    Type,
)

from neo4j.types import INT64_MAX, INT64_MIN


class Attr:
    """Python representation of Neo4j attributes"""
    entity: Type = None
    prop_name: str = None
    types: Iterable[Type] = ()

    def __init__(self, prop_name: str = None):
        if prop_name is not None:
            self.prop_name = prop_name

    @classmethod
    def check_type(cls, value) -> bool:
        """Check if the value matches allowed types"""
        return any(isinstance(value, t) for t in cls.types)

    @classmethod
    def check_constraints(cls, _value) -> bool:
        """Check if the value matches Neo4j constraints"""
        return True

    @classmethod
    def check(cls, value):
        """Perform all check in the right order"""
        return all(f(value) for f in (
            cls.check_type,
            cls.check_constraints,
        ))

    def _compare(self, other: Any, operator: str) -> 'Comparison':
        return Comparison(attribute=self, operator=operator, other=other)

    __eq__: Callable[[], 'Comparison'] = partialmethod(_compare, operator='=')
    __ne__: Callable[[], 'Comparison'] = partialmethod(_compare, operator='<>')


class AnyAttr(Attr):
    """Any Neo4j attribute type"""
    @classmethod
    def check_type(cls, _value) -> bool:
        """Any type is fine"""
        return True


class Comparison(NamedTuple):
    """Data needed to build a comparison"""
    attribute: Attr  # the attribute being compared
    operator: str  # the comparison operator
    other: Any  # the value to be compared with


class Int(Attr):
    """Integer attribute"""
    types = (int,)

    @classmethod
    def check_constraints(cls, value: int) -> bool:
        return INT64_MIN <= value <= INT64_MAX
