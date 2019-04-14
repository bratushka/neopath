from typing import (
    Optional,
    Type,
    Union,
)

from .entities import Node
from .logic import Logic

NodeType = Type[Node]
LabelsDescriptor = Union[str, NodeType, Logic]


class Query:
    def match(self, label: Optional[LabelsDescriptor], var: str) -> 'Query':
        raise NotImplementedError

    def by(self, label: Optional[LabelsDescriptor], var: str) -> 'Query':
        raise NotImplementedError

    def with_(self, label: Optional[LabelsDescriptor], var: str) -> 'Query':
        raise NotImplementedError

    def to(self, label: Optional[LabelsDescriptor], var: str) -> 'Query':
        raise NotImplementedError

    def thru(self, *_, **__) -> 'Query':
        raise NotImplementedError
