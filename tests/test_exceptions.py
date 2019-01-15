"""Tests for neopath.exceptions"""
from unittest import TestCase

from neopath.exceptions import NeopathException


class ExceptionsTests(TestCase):
    """Sample tests"""
    def test(self):
        """Test NeopathException"""
        with self.assertRaisesRegex(NeopathException, NeopathException.message):
            raise NeopathException

        with self.assertRaisesRegex(NeopathException, 'blah'):
            raise NeopathException('blah')
