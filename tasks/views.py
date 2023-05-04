import logging

from rest_framework import generics

from tasks import serializers
from tasks.models import Task
from tasks.models import Employee

logger = logging.getLogger(__name__)


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
