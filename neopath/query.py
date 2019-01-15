"""Query builder"""
from itertools import count, product
from string import ascii_lowercase
from typing import (
    Any,
    Callable,
    Iterator,
    Mapping,
    NamedTuple,
    NoReturn,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
)

from . import attributes, entities, exceptions


NodeIdentifier = Union[Type[entities.Node], str]
EdgeIdentifier = Union[Type[entities.Edge], str]
EntityIdentifier = Union[NodeIdentifier, EdgeIdentifier]
WhereStatement = Union[str, attributes.Comparison]
Conditions = Tuple['Condition', ...]
Rows = Tuple['Row', ...]

START_WITH_MATCH = 'A matching query should start with a `match` method'
EDGE_BEFORE_NODE = 'Two nodes should be connected through an edge'
EDGE_AFTER_EDGE = 'Edge can not exist right after another edge'
DOUBLE_MATCH = 'Method `match` can only be used once per query'


def mapper_builder(identifier: EntityIdentifier) -> Callable:
    """Build a mapper from an EntityIdentifier"""
    return lambda: identifier


def inline_identifier_builder(identifier: EntityIdentifier) -> str:
    """Build an inline_identifier from an EntityIdentifier"""
    if isinstance(identifier, str):
        return '' if not identifier else ':' + identifier
    if issubclass(identifier, entities.Node):
        return ':' + ':'.join(identifier.neo.labels)
    if issubclass(identifier, entities.Edge):
        return ':' + identifier.neo.type
    raise NotImplementedError


def vars_generator(taken: Set[str] = None) -> Iterator[str]:
    """Generate an iterator of: a, b, ..., z, aa, ab, ..."""
    taken = taken or set()

    for i in count(1):
        for letters in product(ascii_lowercase, repeat=i):
            var = ''.join(letters)
            if var in taken:
                continue

            yield var


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

    def _add_row(self, row: Row) -> 'Query':
        """Add a row to the table returning a copied Query object"""
        return self.copy(table=(*self.table, row))

    def _check_integrity(self, is_node: bool) -> NoReturn:
        """Query should be a chain of node-edge-node-edge-..."""
        if not self.table:
            raise exceptions.BadQuery(START_WITH_MATCH)

        if is_node:
            if len(self.table) % 2:
                raise exceptions.BadQuery(EDGE_BEFORE_NODE)
        else:
            if not len(self.table) % 2:
                raise exceptions.BadQuery(EDGE_AFTER_EDGE)

    def connected_through(  # pylint: disable=too-many-arguments
            self,
            identifier: EdgeIdentifier,
            var: Optional[str] = None,
            min_hops: int = None,
            max_hops: int = None,
            _node_types: NodeIdentifier = entities.Node,
    ) -> 'Query':
        """Add an edge to the query"""
        self._check_integrity(False)

        # @TODO: add node_types to the conditions
        # @TODO: check hops values
        hops = '' if min_hops is None and max_hops is None else '*%s..%s' % (
            '' if min_hops is None else str(min_hops),
            '' if max_hops is None else str(max_hops),
        )

        row = Row(
            mapper=mapper_builder(identifier),
            inline_identifier=inline_identifier_builder(identifier),
            var=var,
            hops=hops,
        )

        return self._add_row(row)

    def _by_with_to(
            self,
            direction: Optional[bool],
            identifier: NodeIdentifier,
            var: Optional[str],
    ) -> 'Query':
        """Add a node to the query"""
        row = Row(
            mapper=mapper_builder(identifier),
            inline_identifier=inline_identifier_builder(identifier),
            var=var,
            direction=direction,
        )

        return self._add_row(row)

    def to(  # pylint: disable=invalid-name
            self,
            identifier: NodeIdentifier,
            var: Optional[str] = None,
    ) -> 'Query':
        """
        Add the`end` node to the query.

        The query will look like ()-[]->(this_node).
        """
        self._check_integrity(True)

        return self._by_with_to(True, identifier, var)

    def by(  # pylint: disable=invalid-name
            self,
            identifier: NodeIdentifier,
            var: Optional[str] = None,
    ) -> 'Query':
        """
        Add the`start` node to the query.

        The query will look like ()<-[]-(this_node).
        """
        self._check_integrity(True)

        return self._by_with_to(False, identifier, var)

    def with_(
            self,
            identifier: NodeIdentifier,
            var: Optional[str] = None,
    ) -> 'Query':
        """
        Add a node to the query.

        The query will look like ()-[]-(this_node).
        """
        self._check_integrity(True)

        return self._by_with_to(None, identifier, var)

    def match(
            self,
            identifier: NodeIdentifier,
            var: Optional[str] = None,
    ) -> 'Query':
        """
        Start a MATCH query.
        """
        if self.table:
            raise exceptions.BadQuery(DOUBLE_MATCH)

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
        vars_iterator = vars_generator({
            row.var[1:]
            for row in self.table
            if row.var and row.var.startswith('_')
        })
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

        def stringify_match(start: Row, edge: Row, end: Row) -> str:
            return '(%s%s)%s-[%s%s%s]-%s(%s%s)' % (
                start.var,
                start.inline_identifier,
                '<' if end.direction is False else '',

                edge.var,
                edge.inline_identifier,
                edge.hops,

                '>' if end.direction is True else '',
                end.var,
                end.inline_identifier,
            )

        matches = map(
            lambda q: stringify_match(*q),
            (table[i:i+3] for i in range(0, len(table) - 1, 2)),
        )
        wheres = tuple(c.build(table[c.row].var) for c in conditions)
        returns = sorted({row.var for row in table})

        return ''.join((
            'MATCH %s' % ',\n      '.join(matches),
            '' if not wheres else '\nWHERE %s' % ',\n  AND '.join(wheres),
            '\nRETURN %s' % ', '.join(returns),
        ))
