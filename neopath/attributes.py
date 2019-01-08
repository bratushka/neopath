"""Attributes for Nodes and Edges"""
from typing import (
    Iterable,
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


class Int(Attr):
    """Integer attribute"""
    types = (int,)

    @classmethod
    def check_constraints(cls, value: int) -> bool:
        return INT64_MIN <= value <= INT64_MAX
