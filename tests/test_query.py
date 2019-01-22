"""Tests for neopath.query"""
from unittest import TestCase

from neopath import attributes, exceptions
from neopath.entities import Edge, Node
from neopath.query import Query, vars_generator


class Tests(TestCase):
    """Test helper functions"""
    def test_vars_generator(self):
        """Test vars_generator creates an appropriate iterator"""
        iterator = vars_generator()

        for char_number in range(ord('a'), ord('z') + 1):
            self.assertEqual(next(iterator), chr(char_number))
        self.assertEqual(next(iterator), 'aa')

    def test_vars_generator_with_taken_vars(self):
        """`vars_generator` should not yield vars already taken"""
        iterator = vars_generator({'a', 'b'})

        for char_number in range(ord('c'), ord('z') + 1):
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

    def test_match_with_edge(self):
        """Test the most basic query with an edge"""
        class SomeNode(Node):
            """Node example"""

        class AnEdge(Edge):
            """Edge example"""

        query = (Query()
                 .match('')
                 .connected_through('')
                 .to('')
                 )
        expected = '\n'.join((
            'MATCH (_a)-[_b]->(_c)',
            'RETURN _a, _b, _c',
        ))
        self.assertEqual(str(query), expected)

        query = (Query()
                 .match(SomeNode)
                 .connected_through(AnEdge)
                 .by(SomeNode)
                 )
        expected = '\n'.join((
            'MATCH (_a:SomeNode)<-[_b:ANEDGE]-(_c:SomeNode)',
            'RETURN _a, _b, _c',
        ))
        self.assertEqual(str(query), expected)

    def test_match_with_hops(self):
        """Test min_hops and max_hops in the `connected_through` method"""
        query = (Query()
                 .match('')
                 .connected_through('', min_hops=1)
                 .to('')
                 .connected_through('', max_hops=3)
                 .to('')
                 .connected_through('', min_hops=1, max_hops=3)
                 .to('')
                 .connected_through('')
                 .to('')
                 )
        expected = '\n'.join((
            'MATCH _d = (_a)-[*1..]->(_e),',
            '      _h = (_e)-[*..3]->(_i),',
            '      _l = (_i)-[*1..3]->(_m),',
            '      (_m)-[_n]->(_o)',
            'WITH *, relationships(_d) AS _b, nodes(_d)[1..-1] AS _c,',
            '        relationships(_h) AS _f, nodes(_h)[1..-1] AS _g,',
            '        relationships(_l) AS _j, nodes(_l)[1..-1] AS _k',
            'RETURN _a, _b, _c, _e, _f, _g, _i, _j, _k, _m, _n, _o',
        ))

        self.assertEqual(str(query), expected)

    def test_where_with_edge(self):
        """Check the .where() method with a Node as a parameter"""
        class SomeNode(Node):
            """Node example"""
            attr = attributes.AnyAttr(prop_name='node_name')

        class SomeEdge(Edge):
            """Edge example"""
            attr = attributes.AnyAttr(prop_name='edge_name')

        query = (Query()
                 .match(SomeNode, 'f')
                 .where(SomeNode.attr == 2)
                 .connected_through(SomeEdge, '_a')
                 .where(SomeEdge.attr != '2')
                 .with_('')
                 )
        expected = '\n'.join((
            'MATCH (f:SomeNode)-[_a:SOMEEDGE]-(_b)',
            'WHERE f.node_name = $a,',
            '  AND _a.edge_name <> $b',
            'RETURN _a, _b, f',
        ))
        self.assertEqual(str(query), expected)

        expected = {'a': 2, 'b': '2'}
        self.assertEqual(query.get_vars(), expected)

    # def test_match_one_of_entities(self):
    #     """Should match an arbitrary number of labels or types"""

    def test_bad_chain_query(self):
        """
        Check if match/to/by/with_/connected_through statements are being
         applied in a correct order
        """
        for method in ('with_', 'to', 'by', 'connected_through'):
            with self.assertRaisesRegex(
                    exceptions.BadQuery,
                    r'A matching query should start with a `match` method',
            ):
                getattr(Query(), method)('')

        for method in ('with_', 'to', 'by'):
            with self.assertRaisesRegex(
                    exceptions.BadQuery,
                    r'Two nodes should be connected through an edge',
            ):
                getattr(Query().match(''), method)('')

        with self.assertRaisesRegex(
                exceptions.BadQuery,
                r'Edge can not exist right after another edge',
        ):
            Query().match('').connected_through('').connected_through('')

        with self.assertRaisesRegex(
                exceptions.BadQuery,
                r'Method `match` can only be used once per query',
        ):
            Query().match('').match('')
