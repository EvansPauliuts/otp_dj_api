# Generated by Django 5.0.2 on 2024-02-21 11:33

import api.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pendinguser',
            name='phone',
            field=models.CharField(max_length=19, validators=[api.utils.PhoneValidator()]),
        ),
    ]
