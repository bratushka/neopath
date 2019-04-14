from . import comparisons


class Prop:
    comparable = comparisons.ComparableProp

    def __init__(
            self,
            prop_name: str = None,
            **__,
    ):
        self.entity = None
        self.prop_name = prop_name

    def __call__(self, var: str) -> comparable:
        raise NotImplementedError
        # return self.comparable(var, self.prop_name)
