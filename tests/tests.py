import pytest
from datetime import datetime, timedelta
from core.models.task import Task
from core.builders.task_builder import TaskBuilder
from core.facades.task_facade import TaskPlannerFacade
from core.strategies.last_created import LastCreatedStrategy
from core.strategies.priority_first import PriorityFirstStrategy
from core.strategies.earliest_due import EarliestDueStrategy


def test_task_creation():
    task = Task("Test Task", "Description", "1", datetime.now())
    assert task.name == "Test Task"
    assert task.description == "Description"
    assert task.priority == "1"
    assert not task.status


def test_task_default_status():
    task = Task("Test Task", "Description", "1", datetime.now())
    assert not task.status


def test_task_default_created_at():
    task = Task("Test Task", "Description", "1", datetime.now())
    assert isinstance(task.created_at, datetime)


def test_task_builder():
    task = Task("", "", "", None)
    builder = TaskBuilder(task)
    task = (
        builder.set_name("Task 1")
        .set_description("Description")
        .set_priority("1")
        .set_due_date(datetime.now())
        .build()
    )
    assert task.name == "Task 1"
    assert task.description == "Description"
    assert task.priority == "1"


def test_task_builder_default_values():
    task = Task("", "", "", None)
    builder = TaskBuilder(task)
    task = builder.set_name("Task 1").build()
    assert task.name == "Task 1"
    assert task.description == ""
    assert task.priority == ""


@pytest.fixture
def task_facade():
    return TaskPlannerFacade(strategy=LastCreatedStrategy())


def test_add_task(task_facade):
    task = Task("Task 1", "Description", "1", datetime.now())
    task_facade.add_task(task)
    assert len(task_facade.tasks) == 1


def test_get_all_tasks(task_facade):
    task1 = Task("Task 1", "Description", "1", datetime.now())
    task2 = Task("Task 2", "Description", "2", datetime.now())
    task_facade.add_task(task1)
    task_facade.add_task(task2)
    tasks = task_facade.get_all_tasks()
    assert len(tasks) == 2


def test_set_strategy(task_facade):
    task_facade.set_strategy(PriorityFirstStrategy())
    assert isinstance(task_facade.strategy, PriorityFirstStrategy)


def test_mark_done(task_facade):
    task = Task("Task 1", "Description", "1", datetime.now())
    task_facade.add_task(task)
    task_facade.mark_done("Task 1")
    assert task.status


@pytest.fixture
def sample_tasks():
    task1 = Task("Task 1", "Description", "1", datetime.now())
    task2 = Task("Task 2", "Description", "2", datetime.now() + timedelta(days=1))
    task3 = Task("Task 3", "Description", "3", datetime.now() - timedelta(days=1))
    return [task1, task2, task3]


def test_last_created_strategy(sample_tasks):
    strategy = LastCreatedStrategy()
    sorted_tasks = strategy(sample_tasks)
    assert sorted_tasks[0].name == "Task 1"


def test_priority_first_strategy(sample_tasks):
    strategy = PriorityFirstStrategy()
    sorted_tasks = strategy(sample_tasks)
    assert sorted_tasks[0].name == "Task 1"


def test_earliest_due_strategy(sample_tasks):
    strategy = EarliestDueStrategy()
    sorted_tasks = strategy(sample_tasks)
    assert sorted_tasks[0].name == "Task 3"


def test_integration():
    facade = TaskPlannerFacade(strategy=PriorityFirstStrategy())
    task1 = Task("Task 1", "Description", "3", datetime.now())
    task2 = Task("Task 2", "Description", "1", datetime.now())
    facade.add_task(task1)
    facade.add_task(task2)
    tasks = facade.get_all_tasks()
    assert tasks[0].name == "Task 2"

def test_add_duplicate_task(task_facade):
    task = Task("Task 1", "Description", "1", datetime.now())
    task_facade.add_task(task)
    task_facade.add_task(task)  # Add duplicate
    assert len(task_facade.tasks) == 1  # Ensure no duplicates


def test_mark_done_non_existent_task(task_facade):
    task_facade.mark_done("Non-existent Task")
    assert len(task_facade.tasks) == 0  # Ensure no changes


def test_change_strategy_dynamically(task_facade):
    task1 = Task("Task 1", "Description", "3", datetime.now())
    task2 = Task("Task 2", "Description", "1", datetime.now())
    task_facade.add_task(task1)
    task_facade.add_task(task2)
    task_facade.set_strategy(PriorityFirstStrategy())
    tasks = task_facade.get_all_tasks()
    assert tasks[0].name == "Task 2"  # Verify sorting by priority


def test_empty_task_list(task_facade):
    tasks = task_facade.get_all_tasks()
    assert tasks == []  # Ensure empty list is returned


def test_task_builder_invalid_data():
    task = Task("", "", "", None)
    builder = TaskBuilder(task)
    task = builder.set_name("").set_priority("").build()
    assert task.name == ""  # Ensure invalid data is handled
    assert task.priority == ""


def test_sorting_with_mixed_priorities(task_facade):
    task1 = Task("Task 1", "Description", "3", datetime.now())
    task2 = Task("Task 2", "Description", "1", datetime.now())
    task3 = Task("Task 3", "Description", "2", datetime.now())
    task_facade.add_task(task1)
    task_facade.add_task(task2)
    task_facade.add_task(task3)
    task_facade.set_strategy(PriorityFirstStrategy())
    tasks = task_facade.get_all_tasks()
    assert [t.name for t in tasks] == ["Task 2", "Task 3", "Task 1"]


def test_earliest_due_same_dates(task_facade):
    due_date = datetime.now()
    task1 = Task("Task 1", "Description", "1", due_date)