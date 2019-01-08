"""Tests for neopath.db"""
from unittest import TestCase

from neopath.db import DB


class DBTests(TestCase):
    """Sample tests"""
    def test_match(self):
        """Test example"""
        self.assertIs(DB, DB)
