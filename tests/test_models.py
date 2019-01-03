from unittest import TestCase

from neopath.models import Entity


class Tests(TestCase):
    def test(self):
        """Do nothing"""
        self.assertIs(Entity, Entity)
