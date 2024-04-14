# Generated by Django 5.0.2 on 2024-04-14 04:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("attendance", "0005_absenceaccrual_user_attendance_info"),
    ]

    operations = [
        migrations.AlterField(
            model_name="absenceaccrual",
            name="attendance",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="attendance.attendance_info",
                verbose_name="出席記録",
            ),
        ),
    ]