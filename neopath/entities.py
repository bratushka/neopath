"""Module containing entities"""
import collections
from typing import (
    Tuple,
    Type,
    Union,
)

from . import attributes, exceptions


Identifier = Union[str, 'MetaEntity', 'Logic']


def inline_identifier_builder(identifier: Identifier) -> str:
    """Build an inline_identifier from an EntityIdentifier"""
    if isinstance(identifier, str):
        return '' if not identifier else ':' + identifier
    if isinstance(identifier, MetaNode):
        return ':' + ':'.join(identifier.neo.labels)
    if isinstance(identifier, MetaEdge):
        return ':' + identifier.neo.type
    raise NotImplementedError


class BitwiseMixin:
    """Mixin for &, |, ^ and ~ operators"""
    def __and__(self, other: Identifier) -> 'And':
        """& operator"""
        return And(self, other)

    def __or__(self, other: Identifier) -> 'Or':
        """| operator"""
        return Or(self, other)

    def __xor__(self, other: Identifier) -> 'Xor':
        """^ operator"""
        return Xor(self, other)

    # def __invert__(self):
    #     """~ operator"""
    #     raise NotImplementedError


class Logic(BitwiseMixin):
    """A generic for classes Or, And, Xor, ..."""
    identifiers = ()

    def __init__(
            self,
            first: 'BitwiseMixin',
            _second: Identifier,
    ):
        self.is_node = isinstance(first, MetaNode)\
                       or getattr(first, 'is_node', False)

    def condition_for(self, var: str) -> str:
        """Generate a WHERE statement for variable `var`"""
        raise NotImplementedError

    def inline_for(self, var: str) -> str:
        """Generate an inline identifier for variable `var`"""
        raise NotImplementedError


class And(Logic):
    """AND operator"""
    def __init__(
            self,
            first: 'BitwiseMixin',
            second: Identifier,
    ):
        super().__init__(first, second)

        if self.is_node:
            for identifier in (first, second):
                if isinstance(identifier, And):
                    self.identifiers += identifier.identifiers
                elif isinstance(identifier, MetaNode):
                    self.identifiers += identifier.neo.labels
                elif isinstance(identifier, str):
                    self.identifiers += (identifier,)
                else:
                    raise NotImplementedError
        else:
            raise exceptions.MultipleEdgeTypes

    def condition_for(self, var: str) -> str:
        """Generate a WHERE statement for variable `var`"""
        return ''

    def inline_for(self, var: str) -> str:
        """Generate an inline identifier for variable `var`"""
        if all(isinstance(label, str) for label in self.identifiers):
            return ':' + ':'.join(self.identifiers)
        raise NotImplementedError


class Or(Logic):
    """OR operator"""
    def __init__(
            self,
            first: 'BitwiseMixin',
            second: Identifier,
    ):
        super().__init__(first, second)

        for identifier in (first, second):
            if isinstance(identifier, Or):
                self.identifiers += identifier.identifiers
            elif isinstance(identifier, MetaEdge):
                self.identifiers += (identifier.neo.type,)
            elif isinstance(identifier, MetaNode):
                self.identifiers += (':'.join(identifier.neo.labels),)
            elif isinstance(identifier, str):
                self.identifiers += (identifier,)
            else:
                raise NotImplementedError

    def condition_for(self, var: str) -> str:
        """Generate a WHERE statement for variable `var`"""
        if not self.is_node:
            return ''

        connector = ') OR (%s:' % var
        return '(' + var + ':' + connector.join(self.identifiers) + ')'

    def inline_for(self, var: str) -> str:
        """Generate an inline identifier for variable `var`"""
        return ':' + '|:'.join(self.identifiers) if not self.is_node else ''


class Xor(Logic):
    """XOR operator"""
    def __init__(
            self,
            first: 'BitwiseMixin',
            second: Identifier,
    ):
        super().__init__(first, second)

        if self.is_node:
            for identifier in (first, second):
                if isinstance(identifier, Xor):
                    self.identifiers += identifier.identifiers
                elif isinstance(identifier, MetaNode):
                    self.identifiers += (':'.join(identifier.neo.labels),)
                elif isinstance(identifier, str):
                    self.identifiers += (identifier,)
                else:
                    raise NotImplementedError
        else:
            raise exceptions.MultipleEdgeTypes

    def condition_for(self, var: str) -> str:
        """Generate a WHERE statement for variable `var`"""
        connector = ') XOR (%s:' % var
        return '(' + var + ':' + connector.join(self.identifiers) + ')'

    def inline_for(self, var: str) -> str:
        """Generate an inline identifier for variable `var`"""
        return ''


class MetaEntity(type, BitwiseMixin):
    """Metaclass for Entity"""
    def __new__(mcs: Type, name: str, bases: Tuple[Type, ...], attrs: dict):
        cls = super().__new__(mcs, name, bases, attrs)

        for (attr_name, attr) in attrs.items():
            if isinstance(attr, attributes.Attr):
                attr.entity = cls
                if attr.prop_name is None:
                    attr.prop_name = attr_name

        return cls


class NeoNode:
    """Neo property for Node"""
    __slots__ = ('labels',)

    def __init__(self, name: str, neo: Type):
        labels = getattr(neo, 'labels', [name])
        if (
                isinstance(labels, str)
                or not isinstance(labels, collections.Iterable)
                or not labels
                or any(not isinstance(label, str) for label in labels)
        ):
            raise exceptions.BadNodeLabels
        self.labels: Tuple[str, ...] = tuple(sorted(labels))


class MetaNode(MetaEntity):
    """Metaclass for Node"""
    def __new__(mcs: Type, name: str, bases: Tuple[Type, ...], attrs: dict):
        """Remove `Neo` attribute, add `neo`"""
        neo = attrs.pop('Neo', None)
        cls = super().__new__(mcs, name, bases, attrs)

        cls.neo = NeoNode(cls.__name__, neo)

        return cls


class NeoEdge:
    """Neo property for Edge"""
    __slots__ = ('type',)

    def __init__(self, name: str, neo: Type):
        edge_type = getattr(neo, 'type', name.upper())
        if not isinstance(edge_type, str):
            raise exceptions.BadEdgeType
        self.type: str = edge_type


class MetaEdge(MetaEntity):
    """Metaclass for Edge"""
    def __new__(mcs: Type, name: str, bases: Tuple[Type, ...], attrs: dict):
        """Remove `Neo` attribute, add `neo`"""
        neo = attrs.pop('Neo', None)
        cls = super().__new__(mcs, name, bases, attrs)

        cls.neo = NeoEdge(cls.__name__, neo)

        return cls


# class Entity():
#     """Base class for all nodes and edges."""


class Node(metaclass=MetaNode):
    """Base class for all nodes"""


class Edge(metaclass=MetaEdge):
    """Base class for all edges"""
