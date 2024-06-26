# Generated by Django 5.0.4 on 2024-04-24 09:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='userdetail',
            name='role_customer',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userdetail',
            name='role_merchant',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='merchandise',
            name='image_description',
            field=models.ImageField(null=True, upload_to='images/'),
        ),
        migrations.AlterField(
            model_name='merchandise',
            name='online_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='date put online'),
        ),
        migrations.AlterField(
            model_name='merchandise',
            name='text_description',
            field=models.CharField(max_length=4096, null=True),
        ),
        migrations.CreateModel(
            name='DeadOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField()),
                ('total_price', models.IntegerField()),
                ('status_cancelled', models.BooleanField()),
                ('status_finished', models.BooleanField()),
                ('merchandise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.merchandise')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FavoriteMerchandise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('merchandise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.merchandise')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RunningOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField()),
                ('total_price', models.IntegerField()),
                ('status_paid', models.BooleanField()),
                ('status_taken', models.BooleanField()),
                ('status_cancelling', models.BooleanField()),
                ('merchandise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.merchandise')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
