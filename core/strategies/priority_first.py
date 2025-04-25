from core.strategies.default_sort import DefaultSortStrategy


class PriorityFirstStrategy(DefaultSortStrategy):
    """
    Priority First Strategy
    """

    def __call__(self, tasks):
        """
        Sorts tasks based on their priority.
        """
        return sorted(tasks, key=lambda x: x.priority)