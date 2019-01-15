"""Exceptions for neopath module"""


class NeopathException(Exception):
    """Base neopath exception"""
    message = 'Base neopath exception'

    def __init__(self, message: str = None):
        super().__init__()
        self.message = message or self.message

    def __str__(self):
        return self.message


class BadNodeLabels(NeopathException):
    """Wrong `labels` property assigned to a NeoNode class"""
    message = 'Neo.labels should be an iterable of strings and not a string'


class BadEdgeType(NeopathException):
    """Wrong `type` property assigned to a NeoType class"""
    message = 'Neo.type should be a string'


class BadQuery(NeopathException):
    """Query construction error"""
