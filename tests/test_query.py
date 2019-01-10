"""Tests for neopath.query"""
from unittest import TestCase

from neopath import attributes
from neopath.entities import Node
from neopath.query import Query, vars_generator


class Tests(TestCase):
    """Test helper functions"""
    def test_vars_generator(self):
        """Test vars_generator creates an appropriate iterator"""
        iterator = vars_generator()

        for char_number in range(ord('a'), ord('z') + 1):
            self.assertEqual(next(iterator), chr(char_number))
        self.assertEqual(next(iterator), 'aa')


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
        query = (Query()
                 .match('', 'a')
                 .where('exists(a.name)')
                 .where('a.age = 2')
                 )
        expected = '\n'.join((
            'MATCH (a)',
            'WHERE exists(a.name)',
            '  AND a.age = 2',
            'RETURN a',
        ))
        self.assertEqual(str(query), expected)

    def test_where_with_node(self):
        """Check the .where() method with a Node as a parameter"""
        class SomeNode(Node):
            """Node example"""
            attr = attributes.AnyAttr(prop_name='name')

        query = (Query()
                 .match(SomeNode, 'f')
                 .where(SomeNode.attr == 2)
                 .where('exists(f.something)')
                 .where(SomeNode.attr != '2')
                 )
        expected = '\n'.join((
            'MATCH (f:SomeNode)',
            'WHERE f.name = $a',
            '  AND exists(f.something)',
            '  AND f.name <> $b',
            'RETURN f',
        ))
        self.assertEqual(str(query), expected)

        expected = {'a': 2, 'b': '2'}
        self.assertEqual(query.get_vars(), expected)
