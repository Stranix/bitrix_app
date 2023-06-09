import time
import logging
import requests

from config import settings
from tasks.models import TaskStage, TaskStatus, Employee, Task
from tasks.serializers import BitrixTaskSerializer
from tasks.serializers import TaskDetailSerializer

logger = logging.getLogger(__name__)


def fetch_bitrix_tasks_by_responsible_employee(
        employee_bitrix_id: int,
        start_date: str = '2021-08-01',
        limit_task_per_page: int = 25
) -> list[BitrixTaskSerializer]:
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
            if get_task_by_id(int(bitrix_task['ID'])):
                logger.warning('Задача уже есть в базе. Пропускаем')
                continue
            task_serializer = _parse_task_from_bitrix_api_response(bitrix_task)
            if task_serializer:
                tasks.append(task_serializer)

        if not bitrix_api_response.get('next', False):
            break
        current_page += 1
        time.sleep(0.5)

    logger.info('Закончили получение сотрудников с Bitrix API')
    return tasks


def _parse_task_from_bitrix_api_response(
        task: dict) -> BitrixTaskSerializer | None:
    logger.info('Старт парсинга задачи - %s', task['ID'])

    exclude_stage_id = ['2957', '2121']
    exclude_real_status_id = ['4']

    if task['STAGE_ID'] in exclude_stage_id:
        task['STAGE_ID'] = '0'

    if task['REAL_STATUS'] in exclude_real_status_id:
        task['REAL_STATUS'] = '0'

    bitrix_task = {
        'bitrix_id': task['ID'],
        'subject': task['TITLE'],
        'description': task['DESCRIPTION'],
        'stage': task['STAGE_ID'],
        'status': task['REAL_STATUS'],
        'result_comment': '',
        'creator': task['CREATED_BY'],
        'responsible': task['RESPONSIBLE_ID'],
        'accomplices': task['ACCOMPLICES'],
        'watchers': task['AUDITORS'],
        'parent_task': task['PARENT_ID'],
        'group_id': task['GROUP_ID'],
        'files_url': '',
        'create_at': task['CREATED_DATE'],
        'start_at': task['CREATED_DATE'],
        'duration_fact_time': task['DURATION_FACT'],
        'last_activity_date': task['ACTIVITY_DATE'],
        'subscribers': task['AUDITORS'],
    }

    closed_by_id = task['CLOSED_BY']

    if closed_by_id:
        bitrix_task['closed_by'] = int(closed_by_id)
        bitrix_task['closed_date_time'] = task['CLOSED_DATE']

    serializer = BitrixTaskSerializer(data=bitrix_task)

    if serializer.is_valid():
        logger.info('Спарсили')
        return serializer

    logger.error('Ошибка парсинга %s', serializer.errors)


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


def task_is_closed(task: Task) -> bool:
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


def get_bitrix_id_rnd_employees() -> list[int]:
    logger.info('Получение сотрудников отдела R&D')
    rnd_employees = Employee.objects.filter(department_id=1)
    bitrix_ids = [emp.btrx_id for emp in rnd_employees]
    logger.debug('Список bitrix_id сотрудников R&D: %s', bitrix_ids)
    return bitrix_ids


def get_task_info_from_bitrix(bitrix_task_id: int):
    method_api = 'task.item.getdata.json'
    url = settings.BITRIX_GET_TASK_HOOK + method_api
    params = {
        'TASKID': bitrix_task_id
    }
    response = requests.get(url, params)
    response.raise_for_status()
    bitrix_task_response = response.json()['result']
    task_responsible = int(bitrix_task_response['RESPONSIBLE_ID'])

    if check_responsible_rnd_depart(task_responsible):
        return bitrix_task_response


def fetch_task_from_bitrix(task_id: int):
    if get_task_by_id(task_id):
        logger.error('Такая задача уже есть в БД')
        return

    bitrix_task_response = get_task_info_from_bitrix(task_id)

    if bitrix_task_response:
        serializer = _parse_task_from_bitrix_api_response(bitrix_task_response)
        return serializer


def check_responsible_rnd_depart(task_responsible: int) -> bool:
    if task_responsible not in get_bitrix_id_rnd_employees():
        logger.warning('Задача не в нашей зоне ответственности. Пропускаем')
        return False
    logger.info('Задача в нашей зоне ответственности')
    return True


def check_changes_in_task(bitrix_task_id: int):
    bitrix_task_response = get_task_info_from_bitrix(bitrix_task_id)
    task_in_bitrix = _parse_task_from_bitrix_api_response(bitrix_task_response)
    task_in_db = get_task_by_id(bitrix_task_id)

    if task_in_bitrix:
        # TODO проверять исполнителя на изменение
        if task_in_db.responsible.btrx_id != task_in_bitrix.data.get('responsible'):
            logger.info('У задачи изменился исполнитель')
        # TODO проверять список наблюдателей на изменение

        # TODO проверять тему задачи на изменение
        if task_in_db.subject != task_in_bitrix.data.get('subject'):
            logger.info('Произошло изменение темы задачи')

        # TODO проверять описание задачи на изменение
        if task_in_db.description != task_in_bitrix.data.get('description'):
            logger.info('Произошло изменение описания задачи')

        # TODO проверять изменение статуса задачи
        if task_in_db.status.btrx_status_id != task_in_bitrix.data.get('status'):
            logger.info('Произошла смена статуса задачи')

        # TODO проверять изменения канбан стадии задачи
        if task_in_db.stage.btrx_stage_id != task_in_bitrix.data.get('stage'):
            logger.info('Произошла смена стадии задачи')

    task_in_bitrix.is_valid(raise_exception=True)
    task_in_bitrix.update(task_in_db, task_in_bitrix.validated_data)
