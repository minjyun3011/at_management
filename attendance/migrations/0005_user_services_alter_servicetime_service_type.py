# Generated by Django 5.0.2 on 2024-06-21 09:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("attendance", "0004_servicetime"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="services",
            field=models.ManyToManyField(
                related_name="users",
                to="attendance.servicetime",
                verbose_name="利用するサービス",
            ),
        ),
        migrations.AlterField(
            model_name="servicetime",
            name="service_type",
            field=models.CharField(
                choices=[
                    ("group_morning", "児童発達支援 (午前)"),
                    ("group_afternoon", "児童発達支援 (午後)"),
                    ("individual_morning", "個別（午前）"),
                    ("individual_afternoon", "個別 (午後)"),
                    ("after_school", "放課後デイサービス (個別午後)"),
                ],
                max_length=20,
            ),
        ),
    ]
