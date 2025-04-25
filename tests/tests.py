import pytest
from unittest.mock import MagicMock
from datetime import datetime, timedelta

import main
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
    built = (
        builder.set_name("Task 1")
               .set_description("Description")
               .set_priority("1")
               .set_due_date(datetime.now())
               .set_status(False)
               .build()
    )
    assert built.name == "Task 1"
    assert built.description == "Description"
    assert built.priority == "1"


def test_task_builder_default_values():
    task = Task("", "", "", None)
    builder = TaskBuilder(task)
    built = builder.set_name("Task 1").build()
    assert built.name == "Task 1"
    assert built.description == ""
    assert built.priority == ""
    assert built.due_date is None
    assert not built.status


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


def test_earliest_due_same_dates(task_facade):
    due_date = datetime.now()
    t1 = Task("A", "x", "1", due_date)
    t2 = Task("B", "y", "2", due_date)
    task_facade.add_task(t1)
    task_facade.add_task(t2)
    task_facade.set_strategy(EarliestDueStrategy())
    ordered = task_facade.get_all_tasks()
    assert [t.name for t in ordered] == ["A", "B"]


def test_integration():
    facade = TaskPlannerFacade(strategy=PriorityFirstStrategy())
    task1 = Task("Task 1", "Description", "3", datetime.now())
    task2 = Task("Task 2", "Description", "1", datetime.now())
    facade.add_task(task1)
    facade.add_task(task2)
    tasks = facade.get_all_tasks()
    assert tasks[0].name == "Task 2"


def test_add_duplicate_task(task_facade):
    # two distinct instances with same identity fields
    t1 = Task("Task 1", "Description", "1", datetime.now())
    t2 = Task("Task 1", "Description", "1", datetime.now())
    task_facade.add_task(t1)
    task_facade.add_task(t2)
    assert len(task_facade.tasks) == 1


def test_mark_done_non_existent_task(task_facade):
    task_facade.mark_done("Non-existent Task")
    assert len(task_facade.tasks) == 0


def test_change_strategy_dynamically(task_facade):
    task1 = Task("Task 1", "Description", "3", datetime.now())
    task2 = Task("Task 2", "Description", "1", datetime.now())
    task_facade.add_task(task1)
    task_facade.add_task(task2)
    task_facade.set_strategy(PriorityFirstStrategy())
    tasks = task_facade.get_all_tasks()
    assert tasks[0].name == "Task 2"


def test_empty_task_list(task_facade):
    assert task_facade.get_all_tasks() == []


def test_task_builder_invalid_data():
    task = Task("", "", "", None)
    builder = TaskBuilder(task)
    built = builder.set_name("").set_priority("").build()
    assert built.name == ""
    assert built.priority == ""


def test_mark_undone(task_facade):
    task = Task("Task 1", "Description", "1", datetime.now(), status=True)
    task_facade.add_task(task)
    task_facade.mark_undone("Task 1")
    assert not task.status


def test_main_add_task(monkeypatch):
    spy = MagicMock()
    monkeypatch.setattr(main, 'TaskPlannerFacade', lambda strategy: spy)

    mock_page = MagicMock()
    mock_page.update = MagicMock()

    main.main(mock_page)

    container = mock_page.add.call_args[0][1]
    content = container.content.controls
    title_input, desc_input, prio_input = content[0], content[1], content[2]
    add_btn = content[4].controls[2]

    title_input.value = "Test Task"
    desc_input.value = "Test Description"
    prio_input.value = "1"

    add_btn.on_click(None)

    assert spy.add_task.call_count == 1
    called_task = spy.add_task.call_args[0][0]
    assert called_task.name == "Test Task"
    assert called_task.description == "Test Description"
    assert called_task.priority == 1


def test_main_sort_tasks(monkeypatch):
    spy = MagicMock()
    monkeypatch.setattr(main, 'TaskPlannerFacade', lambda strategy: spy)

    mock_page = MagicMock()
    mock_page.update = MagicMock()

    main.main(mock_page)

    container = mock_page.add.call_args[0][1]
    content = container.content.controls
    action_row = content[4]
    strategy_input = action_row.controls[0]
    sort_btn = action_row.controls[1]

    strategy_input.value = "priority"
    sort_btn.on_click(None)

    spy.set_strategy.assert_called_once()
    args = spy.set_strategy.call_args[0]
    assert isinstance(args[0], PriorityFirstStrategy)
