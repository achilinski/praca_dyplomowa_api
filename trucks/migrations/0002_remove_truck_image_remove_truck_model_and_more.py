# Generated by Django 5.1.2 on 2024-10-15 11:40

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("trucks", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="truck",
            name="image",
        ),
        migrations.RemoveField(
            model_name="truck",
            name="model",
        ),
        migrations.RemoveField(
            model_name="truck",
            name="year",
        ),
    ]
