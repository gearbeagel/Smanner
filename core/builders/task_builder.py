from datetime import datetime

from core.models.task import Task


class TaskBuilder:
    def __init__(self, task: Task):
        self.task = task

    def set_name(self, name: str):
        self.task.name = name
        return self

    def set_description(self, description: str):
        self.task.description = description
        return self

    def set_priority(self, priority: str):
        self.task.priority = priority
        return self

    def set_due_date(self, due_date: datetime):
        self.task.due_date = due_date
        return self

    def set_status(self, status: bool):
        self.task.status = status
        return self

    def build(self) -> Task:
        return self.task

