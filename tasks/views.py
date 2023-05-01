import logging

from tasks.models import Employee
from tasks.models import Task
from tasks.serializers import EmployeeSerializer
from tasks.serializers import TaskSerializer
from rest_framework import generics

logger = logging.getLogger(__name__)


class EmployeesList(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class EmployeeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class TasksList(generics.ListCreateAPIView):
    queryset = Task.objects.all().order_by('-bitrix_id')
    serializer_class = TaskSerializer
