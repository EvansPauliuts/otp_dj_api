# Generated by Django 5.0.2 on 2024-03-13 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_alter_user_session_key"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="session_key",
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]