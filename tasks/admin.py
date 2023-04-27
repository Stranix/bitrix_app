from django.contrib import admin

from .models import Department
from .models import Employee
from .models import TaskStage
from .models import TaskStatus
from .models import Task
from .models import Comment


# Register your models here.

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    pass


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    pass


@admin.register(TaskStage)
class TaskStageAdmin(admin.ModelAdmin):
    pass


@admin.register(TaskStatus)
class TaskStatusAdmin(admin.ModelAdmin):
    pass


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass
