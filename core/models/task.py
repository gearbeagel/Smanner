from dataclasses import dataclass
from datetime import datetime


@dataclass
class Task:
    """
    Represents a task with a name, description, priority, due date, and status.
    """

    name: str
    description: str
    priority: str
    due_date: datetime
    created_at: datetime = datetime.now()
    status: bool = False
