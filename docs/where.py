from datetime import timedelta
from typing import Callable, Tuple, Type, Union


class Logic(tuple):
    pass


class BitwiseMixin:
    __or__ = __xor__ = __and__ = __invert__ = lambda self: Logic()


class Condition(BitwiseMixin):
    def __init__(self, *_, **__):
        pass


class Prop(BitwiseMixin):
    def exists(self) -> Condition:
        return Condition(self)

    def __call__(self, _: str) -> 'Prop':
        return self

    __add__ = __eq__ = __ne__ = starts_with = lambda self, _: self


class MetaEntity(BitwiseMixin):
    pass
    # def __or__(self, other):
    #     pass


class Node(metaclass=MetaEntity):
    def __init__(self, **_):
        pass


class Edge(metaclass=MetaEntity):
    def __init__(self, **_):
        pass


class BusStation(Node):
    city = Prop()


class Airdrome(Node):
    class Neo:
        primary_key = 'iata'

    iata = Prop()
    country_code = Prop()


class Airport(Airdrome):
    name = Prop()
    slogan = Prop()
    motto = Prop()
    terminals = Prop()


class Flight(Edge):
    departure = Prop()
    arrival = Prop()


NodeLabelsDescriptor = Union[
    None,
    str,
    Type[Node],
]


EdgeTypeDescriptor = Union[
    None,
    Type[Edge],
]


EachNextEdge = Callable[[str, str], Condition]


class Query:
    def match(self, _: NodeLabelsDescriptor = None, __: str = None) -> 'Query':
        return self
    to = match

    def con_thru(
            self,
            _: EdgeTypeDescriptor = None,
            __: str = None,
            **___,
    ) -> 'Query':
        return self
        
    def where(self, _: Condition) -> 'Query':
        return self


(Query()
    .match(Airport, 'a')  # Match an airport, from where you can ...
    .con_thru(
        # get a flight ...
        Flight,
        # with maximum 2 stops ...
        max_hops=3,
        # in airports or airdromes ...
        node_types=Airport | Airdrome,
        # only in the countries, which code starts with a 'u' ...
        each_node=lambda a: Airdrome.country_code(a).starts_with('u'),
        # where each next flight should depart at least 1 hour after the
        #  previous flight has arrived ...
        each_next_edge=lambda a, b: Flight.departure(b) >= Flight.arrival(a) + timedelta(hours=1)
    )
    .to(Airport, 'b')  # to some other airport.

    # For some reason we consider departing only from airports having a slogan.
    .where(Airport.slogan('a').exists())
    # But it should have no motto.
    .where(~Airport.motto('a').exists())
    # The destination airport is Aeródromo Cochrane, Chile.
    .where(Airport.iata('b') == 'LGR')
    # The country of departure and the one of arrival should be different.
    .where(Airport.country_code('a') != Airport.country_code('b'))
)

(Query()
    .match(Airport | BusStation)
)


class Node: pass
class And(tuple): pass


# AndNode = Tuple[Node, 'AndNode']
AndNode = And[Union[str, Type[Node], Type['AndNode']], ...]
Ident = Union[str, Type[Node], AndNode]


def q(*_: Ident):
    return 1


q(Node, 'qwe', And(Node, 'asd'))
