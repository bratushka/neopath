"""Query builder"""
from itertools import count, product
from string import ascii_lowercase
from typing import (
    Any,
    Callable,
    Iterator,
    Mapping,
    NamedTuple,
    Optional,
    Tuple,
    Type,
    Union,
)

from . import attributes, entities


NodeIdentifier = Union[Type[entities.Node], str]
EdgeIdentifier = Union[Type[entities.Edge], str]
EntityIdentifier = Union[NodeIdentifier, EdgeIdentifier]
WhereStatement = Union[str, attributes.Comparison]
Conditions = Tuple['Condition', ...]
Rows = Tuple['Row', ...]


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
    """Generate an iterator of: a, b, ..., z, aa, ab, ..."""
    for i in count(1):
        for letters in product(ascii_lowercase, repeat=i):
            yield ''.join(letters)


class Row(NamedTuple):
    """Compositional unit for the Query.table"""
    mapper: Callable  # mapper into Python object for the returned value
    var: str = None  # assigned by user OR when a query construction is done
    inline_identifier: str = ''  # example: ':SomeLabel:OtherLabel'
    direction: bool = None  # True - right, False - left, None - no direction
    hops: str = None  # '' if min and max hops equal 1, else '*min..max'


class Condition(NamedTuple):
    """A `WHERE` condition description"""
    row: int  # Row number to which this condition belongs
    where: WhereStatement = None  # Data to build a condition
    value_var: str = None  # Variable for the cypher statement

    def build(self, var: str) -> str:
        """Compile the condition"""
        if isinstance(self.where, str):
            return self.where
        return '%s.%s %s $%s' % (
            var,
            self.where.attribute.prop_name,
            self.where.operator,
            self.value_var,
        )


class Query:
    """Cypher query builder"""
    def __init__(
            self,
            table: Tuple[Row, ...] = None,
            conditions: Tuple[Condition, ...] = None,
    ):
        self.table = table or ()
        self.conditions = conditions or ()

    def copy(
            self,
            *,
            table: Rows = None,
            conditions: Conditions = None,
    ) -> 'Query':
        """Create an identical copy of self"""
        return Query(table or self.table, conditions or self.conditions)

    def connected_through(  # pylint: disable=too-many-arguments
            self,
            edge: EdgeIdentifier,
            var: Optional[str] = None,
            min_hops: int = None,
            max_hops: int = None,
            node_types: NodeIdentifier = entities.Node,
    ) -> 'Query':
        """Add an edge to the query"""
        # @TODO: check if the node exists before adding edge

        raise NotImplementedError

    def _by_with_to(
            self,
            direction: Optional[bool],
            identifier: NodeIdentifier,
            var: Optional[str],
    ) -> 'Query':
        """Add a node to the query"""
        table = (*self.table, Row(
            mapper=mapper_builder(identifier),
            inline_identifier=inline_identifier_builder(identifier),
            var=var,
            direction=direction,
        ))

        return self.copy(table=table)

    def to(  # pylint: disable=invalid-name
            self,
            identifier: NodeIdentifier,
            var: Optional[str] = None,
    ) -> 'Query':
        """
        Add the`end` node to the query.

        The query will look like ()-[]->(this_node).
        """
        # @TODO: check if the edge exists before adding node

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
        # @TODO: check if the edge exists before adding node

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
        # @TODO: check if the edge exists before adding node

        # return self._by_with_to(None, identifier, var)
        raise NotImplementedError

    def match(
            self,
            identifier: NodeIdentifier,
            var: Optional[str] = None,
    ) -> 'Query':
        """
        Start a MATCH query.
        """
        return self._by_with_to(None, identifier, var)

    def where(self, *conditions: WhereStatement) -> 'Query':
        """Add a `WHERE` statement"""
        query = self

        for condition in conditions:
            query = query.copy(conditions=(
                *query.conditions,
                Condition(row=len(query.table) - 1, where=condition),
            ))

        return query

    def get_table_and_conditions_with_vars(self) -> Tuple[Rows, Conditions]:
        """Populate self.table and self.conditions with appropriate variables"""
        vars_iterator = vars_generator()
        values_iterator = vars_generator()

        # Assign a variable to each Row.
        # noinspection PyProtectedMember
        table = tuple(
            row if row.var else row._replace(var='_' + next(vars_iterator))
            for row in self.table
        )
        # Assign a variable to each Condition if not just a string.
        # noinspection PyProtectedMember
        conditions = tuple(
            condition._replace(value_var=next(values_iterator))
            if isinstance(condition.where, attributes.Comparison) else condition
            for condition in self.conditions
        )

        return table, conditions

    def get_vars(self) -> Mapping[str, Any]:
        """Build a map of variables for the Cypher query"""
        _table, conditions = self.get_table_and_conditions_with_vars()

        return {
            condition.value_var: condition.where.other
            for condition in conditions
            if not isinstance(condition.where, str)
        }

    def __str__(self) -> str:
        """Return a compiled Cypher query"""
        table, conditions = self.get_table_and_conditions_with_vars()

        if len(table) == 1:
            row = table[0]

            if not self.conditions:
                return '\n'.join((
                    'MATCH (%s%s)' % (row.var, row.inline_identifier),
                    'RETURN %s' % row.var
                ))
            return '\n'.join((
                'MATCH (%s%s)' % (row.var, row.inline_identifier),
                'WHERE ' + '\n  AND '.join(
                    c.build(row.var) for c in conditions
                ),
                'RETURN %s' % row.var
            ))

        raise NotImplementedError
