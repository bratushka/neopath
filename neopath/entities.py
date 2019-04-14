from types import DynamicClassAttribute
from typing import Any, FrozenSet, Iterable, Mapping, Tuple, Type

from neo4j.types import graph

from .exceptions import BadLabels
from .logic import BitwiseMixin
from .props import Prop


class MetaEntity(type, BitwiseMixin):
    """Common logic for MetaNode and MetaEdge."""
    def __new__(mcs: Type, name: str, bases: Tuple[Type, ...], attrs: dict):
        # Creation of the entity class.
        cls = super().__new__(mcs, name, bases, attrs)

        # Provide each Prop with an `entity` and a `prop_name`.
        for (attr_name, attr) in attrs.items():
            if isinstance(attr, Prop):
                attr.entity = cls
                if attr.prop_name is None:
                    attr.prop_name = attr_name

        return cls


class MetaNode(MetaEntity):
    """Creator of Node subclasses."""
    def __new__(mcs: Type, name: str, bases: Tuple[Type, ...], attrs: dict):
        # Creation of the Node class.
        class Empty:
            """An empty class."""
        class AutoMeta:
            """Automatically constructed Meta."""
            labels = frozenset((name,))

        class Meta(attrs.pop('Meta', Empty), AutoMeta):
            pass

        if not isinstance(Meta.labels, frozenset):
            Meta.labels = frozenset(Meta.labels)

        cls = super().__new__(mcs, name, bases, attrs)
        cls._meta = Meta

        return cls

    @property
    def labels(cls) -> FrozenSet[str]:
        """Return a tuple of labels"""
        return cls._meta.labels


class MetaEdge(MetaEntity):
    @property
    def type(cls):
        raise NotImplementedError


class Entity:
    def inflate(self, entity: graph.Entity) -> 'Entity':
        raise NotImplementedError

    def as_dict(self) -> Mapping[str, Any]:
        raise NotImplementedError


class Node(Entity, metaclass=MetaNode):
    def __init__(self):
        self._meta = self._meta()

    def _labels_getter(self) -> FrozenSet[str]:
        return self._meta.labels

    def _labels_setter(self, value: Iterable[str]):
        exception_message = BadLabels.__doc__

        try:
            iter(value)
        except TypeError:
            raise BadLabels(exception_message)

        if not value\
                or not all(isinstance(item, str) for item in value)\
                or not all(value):
            raise BadLabels(exception_message)

        labels = frozenset(value)
        if not type(self).labels.issubset(labels):
            raise BadLabels(exception_message)

        self._meta.labels = labels

    labels = DynamicClassAttribute(
        fget=_labels_getter,
        fset=_labels_setter,
    )

    @classmethod
    def inflate(cls, node: graph.Node) -> 'Node':
        raise NotImplementedError

    def save(self):
        raise NotImplementedError


class Edge(Entity, metaclass=MetaEdge):
    @classmethod
    def inflate(cls, edge: graph.Relationship) -> 'Edge':
        raise NotImplementedError

    def start_node(self) -> Node:
        raise NotImplementedError

    def end_node(self) -> Node:
        raise NotImplementedError

    def save(self):
        raise NotImplementedError
