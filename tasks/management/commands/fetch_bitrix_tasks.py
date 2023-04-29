import logging

from django.core.management.base import BaseCommand

from tasks.models import Employee, Task, TaskStage, TaskStatus
from tasks.schemas.BitrixTaskSchema import BitrixTask
from tasks import utils

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        rnd_employees = Employee.objects.filter(department_id=1)
        for employee in rnd_employees:
            tasks = utils.fetch_bitrix_tasks_by_responsible_employee(
                employee.btrx_id
            )
            self._save_in_db(tasks)

    def _save_in_db(self, bitrix_tasks: list[BitrixTask]):
        for bitrix_task in bitrix_tasks:
            if utils.get_task_by_id(bitrix_task.id):
                logger.warning('Задача уже есть в базе. Пропускаем')
                continue

            task_creator = utils.get_employee_by_bitrix_id(
                bitrix_task.created_id
            )

            task_responsible = utils.get_employee_by_bitrix_id(
                bitrix_task.responsible_id
            )

            logger.debug('task_creator: %s', task_creator)
            logger.debug('task_responsible: %s', task_responsible)
            if not task_creator:
                logger.warning(
                    'Не найден постановщик %s',
                    bitrix_task.created_id
                )
                task_creator = utils.get_user_from_bitrix_api(
                    bitrix_task.created_id
                )

            task = Task()
            task.bitrix_id = bitrix_task.id
            task.subject = bitrix_task.subject
            task.description = bitrix_task.description
            task.group_id = bitrix_task.group_id

            task.stage = utils.get_stage_by_btrx_id(
                bitrix_task.stage.value
            )
            task.status = utils.get_status_by_btrx_id(
                bitrix_task.status.value
            )
            task.creator = task_creator
            task.responsible = task_responsible
            task.create_at = bitrix_task.created_date

            if bitrix_task.accomplices:
                task_accomplices = Employee.objects.filter(
                    btrx_id__in=bitrix_task.accomplices
                )
                task.accomplices.set(task_accomplices)

            if bitrix_task.watchers:
                task_watchers = Employee.objects.filter(
                    btrx_id__in=bitrix_task.watchers
                )
                task.watchers.set(task_watchers)

            task.parent_task = bitrix_task.parent_id
            task.group_id = task.group_id if task.group_id else 0
            task.duration_fact_time = bitrix_task.duration_fact_time

            if utils.task_is_closed(bitrix_task):
                task.closed_by = utils.get_employee_by_bitrix_id(
                    bitrix_task.closed_by_id
                )

            if bitrix_task.closed_date_time:
                task.closed_date_time = bitrix_task.closed_date_time
            task.last_activity_date = bitrix_task.last_activity_date

            logger.debug('Перед сохранением: %s', task.__dict__)
            task.save()
