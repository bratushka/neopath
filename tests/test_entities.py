"""Tests for neopath.entities"""
from unittest import TestCase

from neopath import exceptions
from neopath.entities import Edge, Node


class LogicTests(TestCase):
    """Tests for Logic subclasses"""
    def test_simple_and(self):
        """Test basic And logic"""
        class SomeNode(Node):
            """Node example"""
        class OtherNode(Node):
            """Node example"""
            class Neo:
                """Neo example"""
                labels = ('one', 'two')

        class SomeEdge(Edge):
            """Edge example"""
        class OtherEdge(Edge):
            """Edge example"""

        actual = (SomeNode & OtherNode & 'Unexpected')
        condition = ''
        inline = ':SomeNode:one:two:Unexpected'
        self.assertEqual(actual.condition_for('a'), condition)
        self.assertEqual(actual.inline_for('a'), inline)

        with self.assertRaisesRegex(
                exceptions.MultipleEdgeTypes,
                r'An edge should have exactly one type',
        ):
            SomeEdge & OtherEdge  # pylint: disable=pointless-statement

    def test_simple_or(self):
        """Test basic Or logic"""
        class SomeNode(Node):
            """Node example"""
        class OtherNode(Node):
            """Node example"""
            class Neo:
                """Neo example"""
                labels = ('two', 'one')

        class SomeEdge(Edge):
            """Edge example"""
        class OtherEdge(Edge):
            """Edge example"""

        actual = (SomeNode | OtherNode | 'Unexpected')
        condition = '(a:SomeNode) OR (a:one:two) OR (a:Unexpected)'
        inline = ''
        self.assertEqual(actual.condition_for('a'), condition)
        self.assertEqual(actual.inline_for('a'), inline)

        actual = (SomeEdge | OtherEdge | 'Unexpected')
        condition = ''
        inline = ':SOMEEDGE|:OTHEREDGE|:Unexpected'
        self.assertEqual(actual.condition_for('a'), condition)
        self.assertEqual(actual.inline_for('a'), inline)

    def test_simple_xor(self):
        """Test basic Xor logic"""
        class SomeNode(Node):
            """Node example"""
        class OtherNode(Node):
            """Node example"""
            class Neo:
                """Neo example"""
                labels = ('two', 'one')

        class SomeEdge(Edge):
            """Edge example"""
        class OtherEdge(Edge):
            """Edge example"""

        actual = (SomeNode ^ OtherNode ^ 'Unexpected')
        condition = '(a:SomeNode) XOR (a:one:two) XOR (a:Unexpected)'
        inline = ''
        self.assertEqual(actual.condition_for('a'), condition)
        self.assertEqual(actual.inline_for('a'), inline)

        with self.assertRaisesRegex(
                exceptions.MultipleEdgeTypes,
                r'An edge should have exactly one type',
        ):
            SomeEdge ^ OtherEdge  # pylint: disable=pointless-statement


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
