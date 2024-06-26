# Generated by Django 5.0.4 on 2024-05-03 13:05

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_deadorder_added_date_favoritemerchandise_added_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deadorder',
            name='status_cancelled',
        ),
        migrations.RemoveField(
            model_name='deadorder',
            name='status_finished',
        ),
        migrations.AddField(
            model_name='deadorder',
            name='running_added_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name="date added when it's running"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='deadorder',
            name='status',
            field=models.CharField(default='finished', max_length=64),
            preserve_default=False,
        ),
    ]
