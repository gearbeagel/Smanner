from core.strategies.default_sort import DefaultSortStrategy


class EarliestDueStrategy(DefaultSortStrategy):
    """
    Sorts tasks based on the last created date.
    """

    def __call__(self, tasks):
        return sorted(tasks, key=lambda x: x.due_date)