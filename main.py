import flet as ft
from datetime import datetime

from core.builders.task_builder import TaskBuilder
from core.facades.task_facade import TaskPlannerFacade
from core.models.task import Task

from core.strategies.last_created import LastCreatedStrategy
from core.strategies.priority_first import PriorityFirstStrategy
from core.strategies.earliest_due import EarliestDueStrategy


def main(page: ft.Page):
    # Page setup
    page.title = "Smart Task Planner"
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    planner = TaskPlannerFacade(strategy=LastCreatedStrategy())

    title_input = ft.TextField(label="Task Title", width=400)
    description_input = ft.TextField(label="Description", multiline=True, width=400)
    priority_input = ft.Dropdown(
        label="Priority",
        options=[
            ft.dropdown.Option("1", "⚠️ Very High"),
            ft.dropdown.Option("2", "🔥 High"),
            ft.dropdown.Option("3", "✅ Medium"),
            ft.dropdown.Option("4", "😌 Low"),
            ft.dropdown.Option("5", "🧘 Very Low"),
        ],
        value="3",
        width=400
    )

    date_picker = ft.DatePicker()
    due_date_display = ft.Text("No date selected")

    def pick_date(e):
        page.dialog = date_picker
        date_picker.open = True
        page.update()

    def handle_date_change(e):
        if e.control.value:
            due_date_display.value = f"Due: {e.control.value.strftime('%Y-%m-%d')}"
            due_date_display.data = e.control.value  # store date
            page.update()

    date_picker.on_change = handle_date_change

    # Strategy selection
    strategy_input = ft.Dropdown(
        label="Strategy",
        options=[
            ft.dropdown.Option("last_created", "🕒 Last Created"),
            ft.dropdown.Option("priority", "⚠️ Priority First"),
            ft.dropdown.Option("earliest_due", "📅 Earliest Due Date"),
        ],
        value="last_created",
        width=300,
    )

    def sort_tasks(e):
        sel = strategy_input.value
        if sel == "last_created":
            planner.set_strategy(LastCreatedStrategy())
        elif sel == "priority":
            planner.set_strategy(PriorityFirstStrategy())
        elif sel == "earliest_due":
            planner.set_strategy(EarliestDueStrategy())
        refresh_task_list()
        page.update()

    sort_button = ft.ElevatedButton("🔃 Sort Tasks", on_click=sort_tasks)

    task_list_view = ft.Column()

    def add_task(e):
        due_date = due_date_display.data or datetime.now().date()

        _task = Task(name="", description="", priority="", due_date=None, status=False)
        builder = (
            TaskBuilder(_task)
            .set_name(title_input.value)
            .set_description(description_input.value or "No description provided.")
            .set_priority(int(priority_input.value or 3))
            .set_due_date(datetime.combine(due_date, datetime.min.time()))
        )
        task = builder.build()

        planner.add_task(task)

        title_input.value = ""
        description_input.value = ""
        priority_input.value = "3"
        due_date_display.value = "No date selected"
        due_date_display.data = None

        refresh_task_list()
        page.update()

    def refresh_task_list():
        task_list_view.controls.clear()

        tasks = planner.get_all_tasks()

        # Build table rows
        rows = []
        for task in tasks:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Checkbox(value=task.status, on_change=lambda e, t=task: change_status(t))),
                        ft.DataCell(ft.Text(str(task.priority))),
                        ft.DataCell(ft.Text(task.name)),
                        ft.DataCell(ft.Text(task.due_date.strftime("%H:%M, %Y-%m-%d"))),
                    ]
                )
            )

        task_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Done")),
                ft.DataColumn(ft.Text("Priority")),
                ft.DataColumn(ft.Text("Task Name")),
                ft.DataColumn(ft.Text("Due Date")),
            ],
            rows=rows
        )

        task_list_view.controls.append(task_table)

    def change_status(task, status):
        if status:
            planner.mark_done(task.name)
        else:
            planner.mark_undone(task.name)
        refresh_task_list()
        page.update()

    form_column = ft.Column([
        title_input,
        description_input,
        priority_input,
        ft.Row([
            ft.ElevatedButton("📅 Pick Date", on_click=pick_date),
            due_date_display
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([
            strategy_input,
            sort_button,
            ft.ElevatedButton("➕ Add Task", on_click=add_task)
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
    ], alignment=ft.MainAxisAlignment.CENTER)

    page.add(
        ft.Text("Smanner", size=30, weight=ft.FontWeight.BOLD),
        ft.Container(
            content=form_column,
            padding=20,
            width=500,
            alignment=ft.alignment.center
        ),
        ft.Divider(),
        ft.Text("📋 Scheduled Tasks", size=24, weight=ft.FontWeight.BOLD),
        task_list_view,
        date_picker,  # hidden until used
    )

    refresh_task_list()


if __name__ == "__main__":
    ft.app(target=main)
