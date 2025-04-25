# core/strategies/base_strategy.py
from abc import ABC, abstractmethod

class DefaultSortStrategy(ABC):
    """
    Base class for sorting strategies.
    """

    @abstractmethod
    def __call__(self, tasks):
        """
        Sorts the tasks based on the strategy.
        """
        pass