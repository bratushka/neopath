"""Module containing entities"""
import collections
from typing import (
    Tuple,
    Type,
)

from . import attributes, exceptions


class MetaEntity(type):
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

    def __init__(self, name: str, neo: Type = None):
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


# class Entity():
#     """Base class for all nodes and edges."""


class Node(metaclass=MetaNode):
    """Base class for all nodes"""


class Edge:
    """Base class for all edges"""
