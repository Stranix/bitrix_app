import time
import logging
import pydantic
import requests

from config import settings
from tasks.schemas.BitrixTaskSchema import BitrixTask

logger = logging.getLogger(__name__)


def fetch_bitrix_tasks_by_responsible_employee(
        employee_bitrix_id: int,
        start_date: str = '2021-08-01',
        limit_task_per_page: int = 25
) -> list[BitrixTask]:
    logger.info('Start fetch')

    start_page = 1
    url = settings.BITRIX_TASK_HOOK

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

    logger.info('End fetch')
    return tasks


def _parse_task_from_bitrix_api_response(task: dict) -> BitrixTask:
    logger.info('Start parse task')
    try:
        exclude_stage_id = ['2957', '2121']
        exclude_real_status_id = ['4']

        if task['STAGE_ID'] in exclude_stage_id:
            task['STAGE_ID'] = '0'

        if task['REAL_STATUS'] in exclude_real_status_id:
            task['REAL_STATUS'] = '0'

        logger.info('End parse task')
        return BitrixTask(**task)

    except pydantic.error_wrappers.ValidationError as err:
        logger.error(err.args)
