"""Query builder"""
from itertools import count, product
from string import ascii_lowercase
from typing import (
    Callable,
    Iterator,
    # Iterable,
    NamedTuple,
    Optional,
    Tuple,
    Type,
    Union,
)

from . import entities


NodeIdentifier = Union[Type[entities.Node], str]
EdgeIdentifier = Union[Type[entities.Edge], str]
EntityIdentifier = Union[NodeIdentifier, EdgeIdentifier]


def mapper_builder(identifier: EntityIdentifier) -> Callable:
    """Build a mapper from an EntityIdentifier"""
    return lambda: identifier


def inline_identifier_builder(identifier: EntityIdentifier) -> str:
    """Build an inline_identifier from an EntityIdentifier"""
    if isinstance(identifier, str):
        return '' if not identifier else ':' + identifier
    if issubclass(identifier, entities.Node):
        return ':' + ':'.join(identifier.neo.labels)
    raise NotImplementedError


def vars_generator() -> Iterator[str]:
    """Generate an iterator of: _a, _b, ..., _z, _aa, _ab, ..."""
    for i in count(1):
        for letters in product(ascii_lowercase, repeat=i):
            yield ''.join(('_', *letters))


class Row(NamedTuple):
    """Compositional unit for the Query.table"""
    mapper: Callable  # mapper into Python object for the returned value
    var: str = None  # assigned by user OR when a query construction is done
    inline_identifier: str = ''  # example: ':SomeLabel:OtherLabel'
    direction: bool = None  # True - right, False - left, None - no direction
    hops: str = None  # '' if min and max hops equal 1, else '*min..max'


class Query:
    """Cypher query builder"""
    # noinspection PyUnresolvedReferences
    def __init__(self, table: Tuple[Row, ...] = None):
        """
        self.table is a table from which we'll be constructing the query.
        """
        self.table = table or ()

    def connected_through(  # pylint: disable=too-many-arguments
            self,
            edge: EdgeIdentifier,
            var: Optional[str] = None,
            min_hops: int = None,
            max_hops: int = None,
            node_types: NodeIdentifier = entities.Node,
    ) -> 'Query':
        """Add an edge to the query"""
        raise NotImplementedError

    def _by_with_to(
            self,
            direction: Optional[bool],
            identifier: NodeIdentifier,
            var: Optional[str],
    ) -> 'Query':
        table = (*self.table, Row(
            mapper=mapper_builder(identifier),
            inline_identifier=inline_identifier_builder(identifier),
            var=var,
            direction=direction,
        ))
        return Query(table)

    def to(  # pylint: disable=invalid-name
            self,
            identifier: NodeIdentifier,
            var: Optional[str] = None,
    ) -> 'Query':
        """
        Add the`end` node to the query.

        The query will look like ()-[]->(this_node).
        """
        raise NotImplementedError

    def by(  # pylint: disable=invalid-name
            self,
            identifier: NodeIdentifier,
            var: Optional[str] = None,
    ) -> 'Query':
        """
        Add the`start` node to the query.

        The query will look like ()<-[]-(this_node).
        """
        raise NotImplementedError

    def with_(
            self,
            identifier: NodeIdentifier,
            var: Optional[str] = None,
    ) -> 'Query':
        """
        Add a node to the query.

        The query will look like ()-[]-(this_node).
        """
        return self._by_with_to(None, identifier, var)
    match = with_

    def where(self) -> 'Query':
        """Add a `WHERE` statement"""
        raise NotImplementedError

    def __str__(self) -> str:
        """Return a compiled Cypher query"""
        vars_iterator = vars_generator()

        # Assign a variable to each Row.
        # noinspection PyProtectedMember
        table = tuple(
            row if row.var else row._replace(var=next(vars_iterator))
            for row in self.table
        )

        if len(table) == 1:
            row = table[0]

            return '\n'.join((
                'MATCH (%s%s)' % (row.var, row.inline_identifier),
                'RETURN %s' % row.var
            ))

        raise NotImplementedError
