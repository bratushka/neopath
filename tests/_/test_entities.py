"""Tests for neopath.entities"""
from unittest import TestCase

from neopath import exceptions
from neopath.entities import Edge, Node, And, Or, Xor


class LogicTests(TestCase):
    """Tests for Logic subclasses"""
    def test_init(self):
        """Test identifiers composition"""
        or_args = ('this', 'stays')

        actual = And(
            '',  # this should be ignored
            'Some',
            'Some',  # deduplicate
            And('deeply', And(  # all of these should be flattened
                'CONSTRUCTED',
                'Identifier',
            )),
            Or(*or_args),  # this should be added as is
        )
        expected = ('Some', 'deeply', 'CONSTRUCTED', 'Identifier')

        self.assertEqual(actual.identifiers[:-1], expected)
        self.assertIsInstance(actual.identifiers[-1], Or)
        self.assertEqual(actual.identifiers[-1].identifiers, or_args)

    def test_bitwise_operators(self):
        """Bitwise operators should return appropriate Logic instances"""
        class SomeNode(Node):
            """Node example"""

        expected = (SomeNode, 'OtherNode')

        actual = SomeNode & 'OtherNode'
        self.assertIsInstance(actual, And)
        self.assertEqual(actual.identifiers, expected)

        actual = SomeNode | 'OtherNode'
        self.assertIsInstance(actual, Or)
        self.assertEqual(actual.identifiers, expected)

        actual = SomeNode ^ 'OtherNode'
        self.assertIsInstance(actual, Xor)
        self.assertEqual(actual.identifiers, expected)

    def test_and(self):
        """Test And.get_inline_and_where method"""
        class SomeNode(Node):
            """Node example"""
        class OtherNode(Node):
            """Node example"""
        actual = SomeNode & (OtherNode & 'Hello')
        inline, where = actual.get_inline_and_where(True)
        expected_inline = ':SomeNode:OtherNode:Hello'
        expected_where = ''
        self.assertEqual(inline, expected_inline)
        self.assertEqual(where, expected_where)

        with self.assertRaises(exceptions.MultipleEdgeTypes):
            And('any', 'types').get_inline_and_where(False)

    def test_or(self):
        """Test Or.get_inline_and_where method"""
        class SomeNode(Node):
            """Node example"""
        class OtherNode(Node):
            """Node example"""
        actual = SomeNode | (OtherNode | 'Hello')
        inline, where = actual.get_inline_and_where(True)
        expected_inline = ''
        expected_where = '{0}:SomeNode OR {0}:OtherNode OR {0}:Hello'
        self.assertEqual(inline, expected_inline)
        self.assertEqual(where, expected_where)

        class SomeEdge(Edge):
            """Edge example"""
        class OtherEdge(Edge):
            """Edge example"""
        actual = SomeEdge | (OtherEdge | 'Hello')
        inline, where = actual.get_inline_and_where(False)
        expected_inline = ':SOMEEDGE|:OTHEREDGE|:Hello'
        expected_where = ''
        self.assertEqual(inline, expected_inline)
        self.assertEqual(where, expected_where)

    def test_xor(self):
        """Test Xor.get_inline_and_where method"""
        class SomeNode(Node):
            """Node example"""
        class OtherNode(Node):
            """Node example"""
        actual = SomeNode ^ (OtherNode ^ 'Hello')
        inline, where = actual.get_inline_and_where(True)
        expected_inline = ''
        expected_where = '{0}:SomeNode XOR {0}:OtherNode XOR {0}:Hello'
        self.assertEqual(inline, expected_inline)
        self.assertEqual(where, expected_where)

        class SomeEdge(Edge):
            """Edge example"""
        class OtherEdge(Edge):
            """Edge example"""
        actual = SomeEdge ^ (OtherEdge ^ 'Hello')
        inline, where = actual.get_inline_and_where(False)
        expected_inline = ':SOMEEDGE|:OTHEREDGE|:Hello'
        expected_where = ''
        self.assertEqual(inline, expected_inline)
        self.assertEqual(where, expected_where)

    def test_and_or_xor(self):
        """Test Xor.get_inline_and_where method"""
        class SomeNode(Node):
            """Node example"""
        class OtherNode(Node):
            """Node example"""
        # actual = SomeNode | OtherNode & 'Hello' ^ 'World'
        actual = SomeNode | OtherNode & 'Hello' ^ 'World'
        inline, where = actual.get_inline_and_where(True)
        expected_inline = ''
        expected_where = '{0}:SomeNode OR ({0}:OtherNode:Hello XOR {0}:World)'
        self.assertEqual(inline, expected_inline)
        self.assertEqual(where, expected_where)

    def test_complex_logic(self):
        """Test how And, Or and Xor interact with each other"""
        class A(Node):  # pylint: disable=invalid-name
            """Node example"""
        logic_instances = (
            And(And(A, 'B'), Or('C', 'D'), Xor('E', 'F')),
            Or(And('G', 'H'), Or('I', 'J'), Xor('K', 'L')),
            Xor(And('M', 'N'), Or('O', 'P'), Xor('Q', 'R')),
        )
        logic_parts = (
            '{0}:A:B AND ({0}:C OR {0}:D) AND ({0}:E XOR {0}:F)',
            '{0}:G:H OR {0}:I OR {0}:J OR ({0}:K XOR {0}:L)',
            '{0}:M:N XOR ({0}:O OR {0}:P) XOR {0}:Q XOR {0}:R',
        )

        actual = And(*logic_instances)
        inline, where = actual.get_inline_and_where(True)
        expected_inline = ''
        expected_where = '%s AND (%s) AND (%s)' % logic_parts
        self.assertEqual(inline, expected_inline)
        self.assertEqual(where, expected_where)

        actual = Or(*logic_instances)
        inline, where = actual.get_inline_and_where(True)
        expected_inline = ''
        expected_where = '(%s) OR %s OR (%s)' % logic_parts
        self.assertEqual(inline, expected_inline)
        self.assertEqual(where, expected_where)

        actual = Xor(*logic_instances)
        inline, where = actual.get_inline_and_where(True)
        expected_inline = ''
        expected_where = '(%s) XOR (%s) XOR %s' % logic_parts
        self.assertEqual(inline, expected_inline)
        self.assertEqual(where, expected_where)


class NodeNeoTests(TestCase):
    """Tests for Node.neo"""
    def test_neo_property(self):
        """Inheriting from Node should produce a neo property and remove Neo"""
        class SomeNode(Node):
            """Node subclass"""
            class Neo:
                """This class should be removed"""

        self.assertTrue(hasattr(SomeNode, 'neo'))
        self.assertFalse(hasattr(SomeNode, 'Neo'))

    def test_neo_labels(self):
        """Property `neo` should have appropriate labels"""
        class OneNode(Node):
            """Node with no Neo property"""

        self.assertEqual(OneNode.neo.labels, ('OneNode',))

        class TwoNode(Node):
            """Node with a Neo property, but no labels"""
            class Neo:
                """Empty Neo class"""

        self.assertEqual(TwoNode.neo.labels, ('TwoNode',))

        class ThreeNode(Node):
            """Node with a Neo property and labels specified"""
            class Neo:
                """Neo class with labels"""
                labels = ('ThReE', 'Node')

        self.assertEqual(ThreeNode.neo.labels, ('Node', 'ThReE'))

        with self.assertRaises(exceptions.BadNodeLabels):
            # noinspection PyUnusedLocal
            class BadNodeOne(Node):  # pylint: disable=unused-variable
                """Node with a Neo property and labels specified wrongly"""
                class Neo:
                    """Neo class with bad labels"""
                    labels = 'BadNodeOne'

        with self.assertRaises(exceptions.BadNodeLabels):
            # noinspection PyUnusedLocal
            class BadNodeTwo(Node):  # pylint: disable=unused-variable
                """Node with a Neo property and labels specified wrongly"""
                class Neo:
                    """Neo class with bad labels"""
                    labels = None

        with self.assertRaises(exceptions.BadNodeLabels):
            # noinspection PyUnusedLocal
            class BadNodeThree(Node):  # pylint: disable=unused-variable
                """Node with a Neo property and labels specified wrongly"""
                class Neo:
                    """Neo class with bad labels"""
                    labels = (None,)

        with self.assertRaises(exceptions.BadNodeLabels):
            # noinspection PyUnusedLocal
            class BadNodeFour(Node):  # pylint: disable=unused-variable
                """Node with a Neo property and 0 labels"""
                class Neo:
                    """Neo class with bad labels"""
                    labels = ()


class EdgeNeoTests(TestCase):
    """Tests for Edge.neo"""
    def test_neo_labels(self):
        """Property `neo` should have appropriate type"""
        class OneEdge(Edge):
            """Edge with no Neo property"""

        self.assertEqual(OneEdge.neo.type, 'ONEEDGE')

        class TwoEdge(Edge):
            """Edge with a Neo property, but no type"""
            class Neo:
                """Empty Neo class"""

        self.assertEqual(TwoEdge.neo.type, 'TWOEDGE')

        class ThreeEdge(Edge):
            """Edge with a Neo property and a type specified"""
            class Neo:
                """Neo class with a type"""
                type = 'SomeType'

        self.assertEqual(ThreeEdge.neo.type, 'SomeType')

        with self.assertRaises(exceptions.BadEdgeType):
            for type_ in (None, 1, (), {}):
                # noinspection PyUnusedLocal
                class BadEdge(Edge):  # pylint: disable=unused-variable
                    """Node with a Neo property and 0 labels"""
                    class Neo:
                        """Neo class with bad labels"""
                        type = type_
