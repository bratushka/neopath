"""Tests for neopath.db"""
from unittest import TestCase

from neopath.db import DB
from neopath.query import Query


class DBTests(TestCase):
    """Sample tests"""
    def test_match(self):
        """Check if the .match() method returns a Query"""
        class MyDB(DB):
            """Test database"""

        query = MyDB().match('')
        self.assertIsInstance(query, Query)
