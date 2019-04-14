"""Tests for neopath.logic"""
from operator import and_, or_, xor
from unittest import TestCase

from neopath.logic import BitwiseMixin, And, Or, Xor, Not


class BitwiseMixinTest(TestCase):
    """Test &|^~ operators for BitwiseMixin subclasses."""
    @classmethod
    def setUpClass(cls):
        class Class(BitwiseMixin):
            """A BitwiseMixin subclass."""
        cls.first = Class()
        cls.second = Class()

    def test_and_or_xor(self):
        """Test &|^ operators."""
        classes = (And, Or, Xor)
        operators = (and_, or_, xor)

        for cls, operator in zip(classes, operators):
            result = operator(self.first, self.second)

            self.assertIsInstance(result, cls)
            self.assertEqual(result, (self.first, self.second))

    def test_not(self):
        """Test ~ operator."""
        result = ~self.first
        self.assertIsInstance(result, Not)
        self.assertEqual(result, (self.first,))

        result = Not(self.first, self.second)
        self.assertIsInstance(result, Not)
        self.assertEqual(result, (self.first, self.second))
