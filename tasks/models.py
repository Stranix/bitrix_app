from django.db import models


class Department(models.Model):
    name = models.CharField('Название', max_length=35)

    manager = models.ForeignKey(
        'Employee',
        verbose_name='Менеджер отдела',
        related_name='managers',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = 'Отдел'
        verbose_name_plural = 'Отделы'

    def __str__(self):
        return self.name


class Employee(models.Model):
    full_name = models.CharField('ФИО', max_length=100)

    tg_id = models.PositiveIntegerField(
        'Id сотрудника в телеграмме',
        null=True,
        blank=True
    )

    btrx_id = models.PositiveIntegerField(
        'Id сотрудника в Bitrix',
        null=True,
        blank=True
    )

    department = models.ForeignKey(
        Department,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Отдел',
        related_name='employees'
    )

    is_admin = models.BooleanField(
        'Администратор?',
        blank=True,
        default=False
    )

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        department_name = '-'
        if self.department:
            department_name = self.department.name
        return f'{self.full_name} - {department_name}'


class TaskStage(models.Model):
    btrx_stage_id = models.PositiveSmallIntegerField('ID стадии заявки')

    name = models.CharField('Стадия')
    alias = models.CharField(
        'Альяс',
        null=True
    )

    class Meta:
        verbose_name = 'Стадия'
        verbose_name_plural = 'Стадии'

    def __str__(self):
        return '{} - {} - {}'.format(
            self.btrx_stage_id,
            self.alias,
            self.name
        )


class TaskStatus(models.Model):
    btrx_status_id = models.PositiveSmallIntegerField('ID статуса заявки')

    name = models.CharField('Статус')
    alias = models.CharField(
        'Альяс',
        null=True
    )

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'

    def __str__(self):
        return '{} - {} - {}'.format(
            self.btrx_status_id,
            self.alias,
            self.name
        )


class Task(models.Model):
    bitrix_id = models.PositiveIntegerField(
        'ID задачи в Bitrix',
        primary_key=True,
        unique=True,
        db_index=True
    )

    subject = models.CharField('Тема задачи', db_index=True)

    description = models.TextField('Описание задачи')

    stage = models.ForeignKey(
        TaskStage,
        verbose_name='Стадия',
        on_delete=models.DO_NOTHING,
        db_index=True
    )

    status = models.ForeignKey(
        TaskStatus,
        verbose_name='Статус',
        on_delete=models.DO_NOTHING,
        db_index=True
    )

    result_comment = models.TextField(
        'Результат задачи',
        null=True,
        blank=True
    )

    creator = models.ForeignKey(
        Employee,
        verbose_name='Создатель заявки',
        related_name='created_tasks',
        on_delete=models.DO_NOTHING,
        db_index=True
    )

    responsible = models.ForeignKey(
        Employee,
        verbose_name='Ответственный',
        related_name='responsible_tasks',
        on_delete=models.DO_NOTHING,
        db_index=True
    )

    accomplices = models.ManyToManyField(
        Employee,
        verbose_name='Соисполнители',
        related_name='accomplice_tasks',
        db_index=True
    )

    watchers = models.ManyToManyField(
        Employee,
        verbose_name='Наблюдатели',
        related_name='watcher_tasks',
        db_index=True
    )

    parent_task = models.IntegerField(
        'Родительская задача',
        null=True,
        blank=True
    )

    group_id = models.IntegerField('Рабочая группа')

    files_url = models.TextField(
        'Ссылки на вложенные документы',
        null=True,
        blank=True
    )

    create_at = models.DateTimeField('Дата и Время создания заявки')

    start_at = models.DateTimeField(
        'Дата и Время старта задачи',
        null=True,
        blank=True
    )

    duration_fact_time = models.IntegerField(
        'Время потраченное на заявку в минутах',
        null=True,
        blank=True
    )

    closed_by = models.ForeignKey(
        Employee,
        verbose_name='Закрыл задачу',
        related_name='closed_task',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        db_index=True
    )

    closed_date_time = models.DateTimeField(
        'Время и время закрытия задачи',
        null=True,
        blank=True
    )

    last_activity_date = models.DateTimeField(
        'Дата и время последней активности по задаче'
    )

    subscribers = models.ManyToManyField(
        Employee,
        verbose_name='Подписчики на рассылку по задаче'
    )

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        return '{} - {}'.format(
            self.bitrix_id,
            self.subject
        )


class Comment(models.Model):
    author = models.ForeignKey(
        Employee,
        verbose_name='Автор',
        related_name='comments',
        on_delete=models.DO_NOTHING,
        db_index=True
    )

    task = models.ForeignKey(
        Task,
        verbose_name='Задача',
        related_name='comments',
        on_delete=models.DO_NOTHING,
        db_index=True
    )

    message = models.TextField('Текст')

    create_at = models.DateTimeField('Дата создания комментария')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return '{} - {} - {}'.format(
            self.author,
            self.task.subject,
            self.task.create_at
        )
