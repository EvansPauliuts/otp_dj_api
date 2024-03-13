# Generated by Django 5.0.2 on 2024-03-13 10:52

import core.utils.helpers
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("location", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="locationcontact",
            name="phone",
            field=models.CharField(
                blank=True,
                max_length=19,
                validators=[core.utils.helpers.PhoneValidator()],
            ),
        ),
    ]
