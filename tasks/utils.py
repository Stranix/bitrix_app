import time
import logging
import pydantic
import requests
from django.db.models import QuerySet

from config import settings
from tasks.models import TaskStage, TaskStatus, Employee, Task
from tasks.schemas.BitrixTaskSchema import BitrixTask

logger = logging.getLogger(__name__)


def fetch_bitrix_tasks_by_responsible_employee(
        employee_bitrix_id: int,
        start_date: str = '2021-08-01',
        limit_task_per_page: int = 25
) -> list[BitrixTask]:
    logger.info('Старт получения сотрудников с Bitrix API')

    start_page = 1

    api_method = 'task.item.list.json'
    url = settings.BITRIX_TASK_HOOK + api_method

    params = {
        'ORDER[]': '',
        'FILTER[>=CREATED_DATE]': start_date,
        'FILTER[RESPONSIBLE_ID]': employee_bitrix_id,
        'PARAMS[NAV_PARAMS][nPageSize]': limit_task_per_page,
        'PARAMS[NAV_PARAMS][iNumPage]': start_page,
        'SELECT[]': '*'
    }

    tasks = []
    current_page = start_page

    while True:
        if current_page > 1:
            params['PARAMS[NAV_PARAMS][iNumPage]'] = current_page

        response = requests.get(url, params=params)
        logger.debug('Status Code %s', response.status_code)
        response.raise_for_status()

        logger.debug('Final URL %s', response.url)
        bitrix_api_response = response.json()

        for bitrix_task in bitrix_api_response['result']:
            tasks.append(
                _parse_task_from_bitrix_api_response(bitrix_task)
            )

        if not bitrix_api_response.get('next', False):
            break
        current_page += 1
        time.sleep(0.5)

    logger.info('Закончили получение сотрудников с Bitrix API')
    return tasks


def _parse_task_from_bitrix_api_response(task: dict) -> BitrixTask:
    logger.info('Старт парсинга задачи - %s', task['ID'])
    try:
        exclude_stage_id = ['2957', '2121']
        exclude_real_status_id = ['4']

        if task['STAGE_ID'] in exclude_stage_id:
            task['STAGE_ID'] = '0'

        if task['REAL_STATUS'] in exclude_real_status_id:
            task['REAL_STATUS'] = '0'

        logger.info('Спарсили')
        return BitrixTask(**task)

    except pydantic.error_wrappers.ValidationError as err:
        logger.error(err.args)


# TODO функция получения стадии по id
def get_stage_by_btrx_id(stage_btrx_id: int) -> TaskStage:
    logger.info('Запрос получения стадии с id %s', stage_btrx_id)
    try:
        return TaskStage.objects.get(btrx_stage_id=stage_btrx_id)
    except TaskStage.DoesNotExist:
        logger.error('Стадии с id %s не существует', stage_btrx_id)


# TODO функция получения статуса по id
def get_status_by_btrx_id(status_btrx_id: int) -> TaskStatus:
    logger.info('Запрос получения статуса с id %s', status_btrx_id)
    try:
        return TaskStatus.objects.get(btrx_status_id=status_btrx_id)
    except TaskStage.DoesNotExist:
        logger.error('Стадии с id %s не существует', status_btrx_id)


# TODO проверка наличие создателя заявки в локальной бд
# TODO получение ответственного из локальной бд
# TODO получение соисполнителей из локальной бд
# TODO получение наблюдателей из локальной бд
def get_employee_by_bitrix_id(employee_btrx_id: int) -> Employee:
    logger.info('Запрос получения сотрудника с id %s', employee_btrx_id)
    try:
        return Employee.objects.get(btrx_id=employee_btrx_id)
    except Employee.DoesNotExist:
        logger.error('Сотрудника с id %s не существует', employee_btrx_id)
        # TODO попробовать получить по нему информацию из Bitrix


def task_is_closed(task: BitrixTask) -> bool:
    logger.info('Проверка задачи на закрытие')
    logger.debug('closed_by_id - %s', task.closed_by_id)
    logger.debug('task.closed_date_time - %s', task.closed_date_time)
    if not task.closed_by_id or not task.closed_date_time:
        return False
    return True


def get_user_from_bitrix_api(user_bitrix_id: int) -> Employee:
    logger.info(
        'Получение неизвестного пользователя %s из Bitrix',
        user_bitrix_id
    )
    method_api = 'user.get.json'
    url = settings.BITRIX_USER_HOOK + method_api
    params = {
        'ID': user_bitrix_id
    }

    response = requests.get(url, params)
    bitrix_api_response = response.json()
    bitrix_user = bitrix_api_response['result'][0]
    user_in_db = save_bitrix_user_in_db(bitrix_user)

    return user_in_db


def save_bitrix_user_in_db(user_from_bitrix: dict) -> Employee:
    logger.info('Сохраняем нового сотрудника в базу')
    user_full_name = '{} {}'.format(
        user_from_bitrix['NAME'],
        user_from_bitrix['LAST_NAME']
    )

    employee = Employee()
    employee.btrx_id = int(user_from_bitrix['ID'])
    employee.full_name = user_full_name
    employee.save()

    return employee


def get_task_by_id(bitrix_task_id: int) -> Task:
    logger.info('Получение задачи с id %s из базы', bitrix_task_id)
    try:
        return Task.objects.get(bitrix_id=bitrix_task_id)
    except Task.DoesNotExist:
        logger.error('Задачи с id %s не существует', bitrix_task_id)
