"""Tests for neopath.attributes"""
from unittest import TestCase

from neo4j.types import INT64_MAX, INT64_MIN

from neopath import attributes, entities


class AttrTests(TestCase):
    """Tests for Attr"""
    def test_attr_entity_and_name(self):
        """Attribute should have `entity` and `name`"""
        class SomeNode(entities.Node):
            """Node example"""
            attr = attributes.Attr()

        self.assertIs(SomeNode.attr.entity, SomeNode)
        self.assertIs(SomeNode.attr.prop_name, 'attr')

    def test_attr_prop_name(self):
        """Check that a proper prop_name is assigned to the attribute"""
        attr = attributes.Attr(prop_name='awesome')

        self.assertIs(attr.prop_name, 'awesome')

    def test_check_types(self):
        """Check .check_types() method"""
        class SomeAttr(attributes.Attr):
            """Attribute example"""
            types = (str, int)

        self.assertTrue(SomeAttr.check_type(''))
        self.assertTrue(SomeAttr.check_type(2))
        self.assertFalse(SomeAttr.check_type(2.))
        self.assertFalse(SomeAttr.check_type(()))

    def test_check_constraints(self):
        """Check .check_constraints(), should be positive if not overwritten"""
        self.assertTrue(attributes.Attr.check_constraints(''))
        self.assertTrue(attributes.Attr.check_constraints(2))
        self.assertTrue(attributes.Attr.check_constraints(2.))
        self.assertTrue(attributes.Attr.check_constraints(()))

    def test_check(self):
        """Method .check() should check the value in all ways"""
        class SomeAttr(attributes.Attr):
            """Attribute example"""
            types = (str,)

            @classmethod
            def check_constraints(cls, value):
                return len(value) <= 1

        attr = SomeAttr()

        self.assertTrue(attr.check('a'))
        self.assertFalse(attr.check('ab'))
        self.assertFalse(attr.check(2))


class IntTests(TestCase):
    """Tests for Int"""
    def test_check_constraints(self):
        """Neo4j int type is i64"""
        self.assertTrue(attributes.Int.check_constraints(INT64_MIN))
        self.assertTrue(attributes.Int.check_constraints(INT64_MAX))

        self.assertFalse(attributes.Int.check_constraints(INT64_MIN - 1))
        self.assertFalse(attributes.Int.check_constraints(INT64_MAX + 1))
