import logging

from django.core.management.base import BaseCommand

from tasks.models import Employee
from tasks import utils

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        rnd_employees = Employee.objects.filter(department_id=1)
        for employee in rnd_employees:
            tasks = utils.fetch_bitrix_tasks_by_responsible_employee(
                employee.btrx_id
            )

            if not tasks:
                logger.warning(
                    'Для сотрудника %s нет новых задач',
                    employee.full_name
                )
                continue

            for task in tasks:
                task.save()
