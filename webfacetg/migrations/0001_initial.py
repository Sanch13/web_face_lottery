# Generated by Django 4.2.16 on 2024-12-09 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Lottery',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
                ('create', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'lotteries',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TelegramUser',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('telegram_id', models.BigIntegerField(blank=True, null=True, unique=True)),
                ('full_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='ФИО')),
                ('full_name_from_tg', models.CharField(blank=True, max_length=255, null=True, verbose_name='ФИО из Телеграма')),
                ('username', models.CharField(blank=True, max_length=255, null=True)),
                ('is_active', models.BooleanField()),
            ],
            options={
                'db_table': 'users',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('ticket_number', models.IntegerField()),
                ('create', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'tickets',
                'managed': False,
            },
        ),
    ]
