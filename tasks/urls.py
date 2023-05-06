from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from tasks import views

urlpatterns = [
    path('employee/', views.EmployeesList.as_view()),
    path('employee/<int:pk>/', views.EmployeeDetail.as_view()),
    path('task/', views.TasksList.as_view()),
    path('task/<int:pk>/', views.TaskDetail.as_view()),
    path('task/hook/new/', views.new_task_action),
    path('task/hook/update/', views.update_task_action),
]

urlpatterns = format_suffix_patterns(urlpatterns)
