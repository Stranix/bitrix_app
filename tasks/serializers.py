import logging

from rest_framework import serializers
from tasks.models import Employee
from tasks.models import Department
from tasks.models import Task

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


class TaskSerializer(serializers.Serializer):
    bitrix_id = serializers.IntegerField()
    subject = serializers.CharField()

    def create(self, validated_data):
        return Task(**validated_data)

    def update(self, instance, validated_data):
        return instance
