import abc


class PlacerStrategy(metaclass=abc.ABCMeta):
    """
    Partitioning and placement is done within a placer stragy.
    ILP Partitioning is done by default, but there are strategies that directly place the DFG.
    """

    @abc.abstractmethod
    def place(self):
        pass
