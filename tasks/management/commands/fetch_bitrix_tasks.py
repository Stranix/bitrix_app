import logging

from django.core.management.base import BaseCommand

from tasks.models import Employee, Task, TaskStage, TaskStatus
from tasks.schemas.BitrixTaskSchema import BitrixTask
from tasks.utils import fetch_bitrix_tasks_by_responsible_employee

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        rnd_employees = Employee.objects.filter(department_id=1)
        for employee in rnd_employees:
            tasks = fetch_bitrix_tasks_by_responsible_employee(
                employee.btrx_id
            )
            self._save_in_db(tasks)

    def _save_in_db(self, tasks: list[BitrixTask]):
        users_not_found = []
        for task in tasks:
            print('Задача - ', task.id)
            print('task_stage - ', task.stage.value)
            print('task_status - ', task.status.value)
            task_stage = TaskStage.objects.get(
                btrx_stage_id=task.stage.value
            )

            task_status = TaskStatus.objects.filter(
                btrx_status_id=task.status.value
            ).first()

            try:
                task_creator = Employee.objects.get(btrx_id=task.created_id)
            except Employee.DoesNotExist:
                users_not_found.append(task.created_id)
                logger.error('Employee with id %s not found', task.created_id)
                continue

            task_responsible = Employee.objects.get(
                btrx_id=task.responsible_id
            )

            task_accomplices = Employee.objects.filter(
                btrx_id__in=task.accomplices
            )

            task_watchers = Employee.objects.filter(
                btrx_id__in=task.watchers
            )

            task_parent = None
            if task.parent_id:
                try:
                    task_parent = Task.objects.get(bitrix_id=task.parent_id)
                except Task.DoesNotExist:
                    logger.warning('Task %s not exist', task.parent_id)

            task_group_id = task.group_id if task.group_id else 0
            task_closed_by = None
            if task.closed_by_id:
                try:
                    task_closed_by = Employee.objects.get(
                        btrx_id=task.closed_by_id
                    )
                except Employee.DoesNotExist:
                    users_not_found.append(task.closed_by_id)
                    logger.error(
                        'Employee with id %s not found',
                        task.closed_by_id
                    )
                    continue

            task_subscribers = task_watchers

            try:
                Task.objects.get(bitrix_id=task.id)
                continue
            except Task.DoesNotExist:
                task_closed_date_time = None if not task.closed_date_time else task.closed_date_time
                task_in_db = Task.objects.create(
                    bitrix_id=task.id,
                    subject=task.subject,
                    description=task.description,
                    stage=task_stage,
                    status=task_status,
                    result_comment=None,
                    creator=task_creator,
                    responsible=task_responsible,
                    parent_task=task_parent,
                    group_id=task_group_id,
                    files_url=None,
                    create_at=task.created_date,
                    start_at=task.created_date,
                    duration_fact_time=task.duration_fact_time,
                    closed_by=task_closed_by,
                    closed_date_time=task_closed_date_time,
                    last_activity_date=task.last_activity_date,
                )

                task_in_db.accomplices.set(task_accomplices)
                task_in_db.watchers.set(task_watchers)
                task_in_db.subscribers.set(task_subscribers)
        print(users_not_found)
