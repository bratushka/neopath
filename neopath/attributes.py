"""Attributes for Nodes and Edges"""


class Attr:
    """Python representation of Neo4j attributes"""
    entity = None
    prop_name = None

    def __init__(self, prop_name: str = None):
        if prop_name is not None:
            self.prop_name = prop_name
