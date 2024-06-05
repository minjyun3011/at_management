# Generated by Django 5.0.2 on 2024-06-05 04:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("attendance", "0002_alter_attendance_info_end_time_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="attendance_info",
            name="inputter",
            field=models.CharField(
                blank=True, max_length=50, null=True, verbose_name="入力者"
            ),
        ),
        migrations.AddField(
            model_name="attendance_info",
            name="updater",
            field=models.CharField(
                blank=True, max_length=50, null=True, verbose_name="更新者"
            ),
        ),
    ]
