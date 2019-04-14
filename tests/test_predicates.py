"""Tests for neopath.predicates"""
from unittest import TestCase

from neopath import predicates


class PredicatesTest(TestCase):
    """Tests for predicates functions."""
    def test_eq(self):
        """Test eq predicate."""
        result = predicates.eq('a', 'b')
        expected = 'a = b'

        self.assertEqual(result, expected)

    def test_ne(self):
        """Test ne predicate."""
        result = predicates.ne('a', 'b')
        expected = 'a <> b'

        self.assertEqual(result, expected)

    def test_starts_with(self):
        """Test starts_with predicate."""
        result = predicates.starts_with('a', 'b')
        expected = 'a STARTS WITH b'

        self.assertEqual(result, expected)

    def test_is_null(self):
        """Test is_null predicate."""
        result = predicates.is_null('a', None)
        expected = 'a IS NULL'

        self.assertEqual(result, expected)

    def test_exists(self):
        """Test starts_with predicate."""
        result = predicates.exists('a', None)
        expected = 'exists(a)'

        self.assertEqual(result, expected)
