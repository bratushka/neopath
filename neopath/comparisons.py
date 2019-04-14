from typing import Any, Callable, Mapping, Optional, Tuple

from . import predicates
from .logic import BitwiseMixin


class Comparison(BitwiseMixin):
    """
    Box.width('q') == 2

    q.width = $a
    {
      'a': 2,
    }
    -----------------------------------------------------
    (Box.width('q') - 3) / 6 == Box.height('q') ** 2

    (q.width - $a) / $b = q.width ^ $c
    {
      'a': 3,
      'b': 6,
      'c': 2,
    }
    """
    def __init__(
            self,
            left: 'ComparableProp',
            statement_builder: Callable[[str, Optional[str]], str],
            right: Any,
    ):
        self.left = left
        self.statement_builder = statement_builder
        self.right = right

    def get_statement_and_values(self) -> Tuple[str, Mapping[str, Any]]:
        raise NotImplementedError


class ComparableProp:
    """An entity property descriptor ready to be compared."""
    def __init__(self, var: str, prop_name: str):
        self.var = var
        self.prop_name = prop_name

    def __eq__(self, other) -> Comparison:
        """A property equality check."""
        return Comparison(
            self,
            predicates.eq,
            other,
        )

    def exists(self) -> Comparison:
        """Checks if the property exists."""
        return Comparison(
            self,
            predicates.exists,
            None,
        )


class ComparableStr(ComparableProp):
    def starts_with(self) -> Comparison:
        raise NotImplementedError
