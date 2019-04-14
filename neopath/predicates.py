def eq(left: str, right: str) -> str:
    """Cypher equality comparison."""
    return left + ' = ' + right


def ne(left: str, right: str) -> str:
    """Cypher inequality comparison."""
    return left + ' <> ' + right


def starts_with(left: str, right: str) -> str:
    """Check if the `left` string starts with the `right` substring."""
    return left + ' STARTS WITH ' + right


def is_null(left: str, _right: None) -> str:
    """Check if the `left` argument doesn't exist."""
    return left + ' IS NULL'


def exists(left: str, _right: None) -> str:
    """Check if the `left` argument exists."""
    return 'exists(%s)' % left
