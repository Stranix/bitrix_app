# Generated by Django 4.2 on 2023-04-27 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_taskstage_alias_taskstatus_alias'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='is_admin',
            field=models.BooleanField(blank=True, default=False, verbose_name='Администратор?'),
        ),
    ]