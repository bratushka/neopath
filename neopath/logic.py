from typing import Union


class BitwiseMixin:
    """A mixin providing support for &|^~ operators."""
    def __and__(self, other) -> 'And':
        return And(self, other)

    def __or__(self, other) -> 'Or':
        return Or(self, other)

    def __xor__(self, other) -> 'Xor':
        return Xor(self, other)

    def __invert__(self) -> 'Not':
        return Not(self)


class Logic(tuple, BitwiseMixin):
    """Common superclass for logical classes: And, Or, Xor, Not."""
    def __new__(cls, *args: Union[str, BitwiseMixin]):
        # noinspection PyTypeChecker
        return tuple.__new__(cls, args)


class And(Logic):
    """Helper class for & operation"""
    pass


class Or(Logic):
    """Helper class for | operation"""
    pass


class Xor(Logic):
    """Helper class for ^ operation"""
    pass


class Not(Logic):
    """Helper class for ~ operation"""
    pass
