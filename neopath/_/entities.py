"""Module containing entities"""
import collections
from typing import (
    Tuple,
    Type,
    Union,
)

from . import attributes, exceptions


Identifier = Union[str, 'BitwiseMixin', Type['Edge'], Type['Node']]


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


class WhereMixin:
    """
    Mixin adding the `get_or_xor_where_part` method.

    ATTENTION: only to be used with Logic subclasses.
    """
    operator = ''

    def get_or_xor_where_part(self, is_node: bool, many: bool) -> str:
        """
        Construct the `where` part of the `get_inline_and_where` for Or and Xor.
        """
        parts = []
        # noinspection PyUnresolvedReferences
        for ident in self.identifiers:
            if isinstance(ident, str):
                parts.append('{0}:' + ident)
            elif isinstance(ident, type) and issubclass(ident, Node):
                parts.append('{0}:' + ':'.join(ident.neo.labels))
            elif isinstance(ident, Logic):
                _inline, _where = ident.get_inline_and_where(is_node, many)
                if _inline:
                    parts.append('{0}%s' % _inline)
                else:
                    parts.append('(' + _where + ')')
            else:
                raise NotImplementedError
        return self.operator.join(parts)


class Logic(BitwiseMixin):
    """A generic for classes Or, And, Xor, ..."""
    def __init__(self, *identifiers: Identifier):
        unique = []
        existing = set()
        for ident in filter(bool, identifiers):
            if ident not in existing:
                existing.add(ident)
                unique.append(ident)

        flattened = []
        for ident in unique:
            if isinstance(ident, self.__class__):
                flattened.extend(ident.identifiers)
            else:
                flattened.append(ident)

        self.identifiers = tuple(flattened)

    def get_inline_and_where(  # pylint: disable=no-self-use
            self,
            _is_node: bool,
            _many: bool = False,
    ) -> Tuple[str, str]:
        """Get the inline identifier and the WHERE statement"""
        raise NotImplementedError


class And(Logic):
    """AND operator"""
    def get_inline_and_where(
            self,
            is_node: bool,
            many: bool = False,
    ) -> Tuple[str, str]:
        """Get the inline identifier and the WHERE statement"""
        if not is_node:
            raise exceptions.MultipleEdgeTypes

        # Inline block
        if all(
                isinstance(i, str)
                or (isinstance(i, type) and issubclass(i, Node))
                for i in self.identifiers
        ):
            parts = []
            for ident in self.identifiers:
                if isinstance(ident, str):
                    parts.append(ident)
                else:
                    parts.extend(ident.neo.labels)
            inline = ':' + ':'.join(parts)

            return inline, ''

        # Where block
        parts = []
        for ident in self.identifiers:
            if isinstance(ident, str):
                parts.append(ident)
            elif isinstance(ident, type) and issubclass(ident, Node):
                parts.extend(ident.neo.labels)
        parts = ['{0}:' + ':'.join(parts)]

        for ident in self.identifiers:
            if isinstance(ident, Logic):
                _inline, _where = ident.get_inline_and_where(is_node, many)
                parts.append('(' + _where + ')')
        where = ' AND '.join(parts)

        return '', where


class Or(Logic, WhereMixin):
    """OR operator"""
    operator = ' OR '

    def get_inline_and_where(
            self,
            is_node: bool,
            many: bool = False,
    ) -> Tuple[str, str]:
        if not is_node:
            parts = []
            for ident in self.identifiers:
                part = ident if isinstance(ident, str) else ident.neo.type
                parts.append(part)
            return ':' + '|:'.join(parts), ''

        return '', self.get_or_xor_where_part(is_node, many)


class Xor(Logic, WhereMixin):
    """XOR operator"""
    operator = ' XOR '

    def get_inline_and_where(
            self,
            is_node: bool,
            many: bool = False,
    ) -> Tuple[str, str]:
        if not is_node:
            return Or(*self.identifiers).get_inline_and_where(is_node, many)

        return '', self.get_or_xor_where_part(is_node, many)


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
