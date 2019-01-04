"""Tests for neopath.query"""
from unittest import TestCase

from neopath.db import DB
from neopath.query import Query, vars_generator


class Tests(TestCase):
    """Test helper functions"""
    def test_vars_generator(self):
        """Test vars_generator creates an appropriate iterator"""
        iterator = vars_generator()

        for char_number in range(ord('a'), ord('z') + 1):
            self.assertEqual(next(iterator), '_' + chr(char_number))
        self.assertEqual(next(iterator), '_aa')


class QueryTests(TestCase):
    """Query tests"""
    def test_simple_match(self):
        """Check the base .with_() method"""
        query = Query(DB()).with_('')
        expected = '\n'.join((
            'MATCH (_a)',
            'RETURN _a',
        ))
        self.assertEqual(str(query), expected)

        query = Query(DB()).with_('SomeLabel')
        expected = '\n'.join((
            'MATCH (_a:SomeLabel)',
            'RETURN _a',
        ))
        self.assertEqual(str(query), expected)

        query = Query(DB()).with_('SomeLabel:OtherLabel')
        expected = '\n'.join((
            'MATCH (_a:SomeLabel:OtherLabel)',
            'RETURN _a',
        ))
        self.assertEqual(str(query), expected)
