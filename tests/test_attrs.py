"""Tests for neopath.attributes"""
from unittest import TestCase

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
