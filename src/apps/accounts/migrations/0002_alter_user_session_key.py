# Generated by Django 5.0.2 on 2024-03-12 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="session_key",
            field=models.CharField(blank=True, max_length=40),
        ),
    ]
