class NeopathException(Exception):
    """Common parent for all neopath exceptions."""


class BadLabels(NeopathException):
    """`labels` should be an iterable of nonempty strings."""
