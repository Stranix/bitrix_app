import logging

from rest_framework import serializers
from tasks.models import Employee
from tasks.models import Department
from tasks.models import Task
from tasks.models import TaskStage
from tasks.models import TaskStatus

logger = logging.getLogger(__name__)


class EmployeeSerializer(serializers.ModelSerializer):
    department = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Department.objects,
        default=None
    )

    class Meta:
        model = Employee
        fields = '__all__'


class TaskListSerializer(serializers.ModelSerializer):
    accomplices = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='full_name'
    )

    watchers = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='full_name'
    )

    class Meta:
        model = Task
        fields = '__all__'


class TaskDetailSerializer(serializers.ModelSerializer):
    accomplices = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='full_name'
    )

    watchers = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='full_name'
    )

    class Meta:
        model = Task
        fields = '__all__'


class BitrixTaskSerializer(serializers.ModelSerializer):
    bitrix_id = serializers.IntegerField()

    stage = serializers.SlugRelatedField(
        queryset=TaskStage.objects,
        slug_field='btrx_stage_id'
    )
    status = serializers.SlugRelatedField(
        queryset=TaskStatus.objects,
        slug_field='btrx_status_id'
    )

    creator = serializers.SlugRelatedField(
        queryset=Employee.objects,
        slug_field='btrx_id'
    )
    responsible = serializers.SlugRelatedField(
        queryset=Employee.objects,
        slug_field='btrx_id'
    )
    accomplices = serializers.SlugRelatedField(
        many=True,
        required=False,
        queryset=Employee.objects,
        slug_field='btrx_id'
    )
    watchers = serializers.SlugRelatedField(
        many=True,
        queryset=Employee.objects,
        slug_field='btrx_id'
    )

    closed_by = serializers.SlugRelatedField(
        required=False,
        queryset=Employee.objects,
        slug_field='btrx_id'

    )

    subscribers = serializers.SlugRelatedField(
        many=True,
        queryset=Employee.objects,
        slug_field='btrx_id'
    )

    class Meta:
        model = Task
        fields = '__all__'
