# Generated by Django 5.0 on 2024-02-12 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resqroute', '0002_alter_connection_destination_alter_connection_source'),
    ]

    operations = [
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dni', models.CharField(max_length=10, unique=True)),
                ('name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=320, unique=True)),
                ('phone_number', models.CharField(max_length=12, unique=True)),
                ('staff_type', models.IntegerField(choices=[(0, 'Brigadista'), (1, 'Profesor')])),
            ],
        ),
    ]
