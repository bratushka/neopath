"""Tests for neopath.query"""
from unittest import TestCase

from neopath.entities import Node
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
        """Check the base .match() method"""
        query = Query().match('')
        expected = '\n'.join((
            'MATCH (_a)',
            'RETURN _a',
        ))
        self.assertEqual(str(query), expected)

        query = Query().match('SomeLabel')
        expected = '\n'.join((
            'MATCH (_a:SomeLabel)',
            'RETURN _a',
        ))
        self.assertEqual(str(query), expected)

        query = Query().match('SomeLabel', 'var')
        expected = '\n'.join((
            'MATCH (var:SomeLabel)',
            'RETURN var',
        ))
        self.assertEqual(str(query), expected)

        query = Query().match('SomeLabel:OtherLabel')
        expected = '\n'.join((
            'MATCH (_a:SomeLabel:OtherLabel)',
            'RETURN _a',
        ))
        self.assertEqual(str(query), expected)

    def test_match_with_node_class(self):
        """Simple match query, but passing a class instead of a string"""
        class OneNode(Node):
            """Node example"""

        query = Query().match(OneNode)
        expected = '\n'.join((
            'MATCH (_a:OneNode)',
            'RETURN _a',
        ))
        self.assertEqual(str(query), expected)

        class TwoNode(Node):
            """Node example"""
            class Neo:
                """Neo with labels"""
                labels = ('Two', 'Node')

        query = Query().match(TwoNode, 'q')
        expected = '\n'.join((
            'MATCH (q:Node:Two)',
            'RETURN q',
        ))
        self.assertEqual(str(query), expected)

    def test_simple_where(self):
        """Check the .where() method with only .match()"""
