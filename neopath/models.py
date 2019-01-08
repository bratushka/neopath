"""Module containing entities"""
import collections
from typing import (
    Tuple,
    Type,
)

from . import exceptions


class NeoEntity:
    """___"""


class NeoNode(NeoEntity):
    """Neo property for Node"""
    __slots__ = ('labels',)

    def __init__(self, name: str, neo: Type = None):
        labels = getattr(neo, 'labels', [name])
        if (
                isinstance(labels, str)
                or not isinstance(labels, collections.Iterable)
                or any(not isinstance(label, str) for label in labels)
        ):
            raise exceptions.BadNodeLabels
        self.labels: Tuple[str, ...] = tuple(sorted(labels))


class MetaNode(type):
    """Metaclass for Entity"""
    def __new__(mcs: Type, name: str, bases: Tuple[Type, ...], attrs: dict):
        """Custom inheritance method"""
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
