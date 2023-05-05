import logging

from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from tasks import serializers
from tasks.models import Task
from tasks.models import Employee
from tasks.utils import fetch_task_from_bitrix, check_changes_in_task

logger = logging.getLogger(__name__)


# TODO обрабатывать веб хук о новой задаче
# TODO обрабатывать веб хух о изменении задачи
# TODO работать с комментариями (получать, добавлять)

class EmployeesList(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer


class EmployeeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer


class TasksList(generics.ListCreateAPIView):
    queryset = Task.objects.prefetch_related(
        'accomplices', 'watchers'
    ).order_by('-bitrix_id')
    serializer_class = serializers.TaskListSerializer


class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.prefetch_related('accomplices', 'watchers')
    serializer_class = serializers.TaskDetailSerializer


@api_view(['POST'])
def new_task_action(request):
    """Входящий веб хук о заведении новой задачи"""
    task_number = int(request.data.get('data[FIELDS_AFTER][ID]'))
    if task_number:
        # получить задачу из битрикс
        serializer = fetch_task_from_bitrix(task_number)

        # сериализовать и если все ок сохранить
        if not serializer:
            return Response({'error': 'nothing to add'})

        serializer.save()
        logger.info('Сохранил задачу в %s БД', task_number)

        # отправить уведомление в телеграм
        logger.info('Отправил уведомление в телеграм')

    return Response({'status': 'ok'})


@api_view(['POST'])
def update_task_action(request):
    task_event = request.data.get('event')
    if task_event == 'ONTASKUPDATE':
        logger.info('Произошло обновление задачи')
        check_changes_in_task(
            int(request.data.get('data[FIELDS_AFTER][ID]'))
        )

    if task_event == 'ONTASKCOMMENTADD':
        logger.info('Добавлен комментарий к задаче')
