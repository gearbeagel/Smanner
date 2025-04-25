from core.strategies.default_sort import DefaultSortStrategy


class TaskPlannerFacade:
    def __init__(self, strategy: DefaultSortStrategy):
        self.tasks = []
        self.strategy = strategy

    def get_all_tasks(self):
        """
        Returns all tasks sorted by the current strategy.
        """
        return self.strategy(self.tasks)

    def add_task(self, task):
        if not any(t.name == task.name for t in self.tasks):
            self.tasks.append(task)

    def set_strategy(self, strategy):
        self.strategy = strategy

    def mark_done(self, task_title):
        for task in self.tasks:
            if task.name == task_title:
                task.status = True

    def mark_undone(self, task_title):
        for task in self.tasks:
            if task.name == task_title:
                task.status = False