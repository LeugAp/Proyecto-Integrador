# Generated by Django 5.0 on 2024-02-13 00:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resqroute', '0003_staff'),
    ]

    operations = [
        migrations.AlterField(
            model_name='functionsbrigade',
            name='function',
            field=models.CharField(max_length=300),
        ),
    ]