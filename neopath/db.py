"""Database related objects"""
from .query import Query


class DB:
    """Database instance representation"""
    def match(self, *args, **kwargs) -> Query:
        """Start a match query"""
        return Query(self).with_(*args, **kwargs)
