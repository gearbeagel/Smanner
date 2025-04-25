from core.strategies.default_sort import DefaultSortStrategy


class LastCreatedStrategy(DefaultSortStrategy):
    """
    Sorts tasks based on the last created date.
    """

    def __call__(self, tasks):
        return sorted(tasks, key=lambda x: x.created_at)