# Generated by Django 5.0.2 on 2024-05-03 06:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Attendance_info",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("calendar_date", models.DateField(verbose_name="日付")),
                ("start_time", models.TimeField(verbose_name="開始時間")),
                ("end_time", models.TimeField(verbose_name="終了時間")),
                (
                    "status",
                    models.CharField(
                        choices=[("PR", "出席"), ("AB", "欠席")],
                        default="PR",
                        max_length=2,
                        verbose_name="出席状態",
                    ),
                ),
                (
                    "transportation_to",
                    models.CharField(
                        choices=[("US", "利用"), ("NU", "未利用")],
                        default="NU",
                        max_length=2,
                        verbose_name="送迎サービス（往路）",
                    ),
                ),
                (
                    "transportation_from",
                    models.CharField(
                        choices=[("US", "利用"), ("NU", "未利用")],
                        default="NU",
                        max_length=2,
                        verbose_name="送迎サービス（復路）",
                    ),
                ),
                (
                    "absence_reason",
                    models.TextField(blank=True, null=True, verbose_name="欠席理由"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="更新日時"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                ("name", models.CharField(max_length=100, verbose_name="氏名")),
                ("birthdate", models.DateField(verbose_name="生年月日")),
                (
                    "gender",
                    models.CharField(
                        choices=[("M", "Male"), ("F", "Female"), ("O", "Other")],
                        default="O",
                        max_length=1,
                        verbose_name="性別",
                    ),
                ),
                (
                    "recipient_number",
                    models.CharField(
                        max_length=20,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                        verbose_name="受給者番号",
                    ),
                ),
                (
                    "education_level",
                    models.CharField(
                        choices=[
                            ("KY", "年少"),
                            ("KM", "年中"),
                            ("KO", "年長"),
                            ("E1", "小学1年"),
                            ("E2", "小学2年"),
                            ("E3", "小学3年"),
                            ("E4", "小学4年"),
                            ("E5", "小学5年"),
                            ("E6", "小学6年"),
                        ],
                        default="KY",
                        max_length=2,
                        verbose_name="教育区分",
                    ),
                ),
                ("welfare_exemption", models.IntegerField(verbose_name="児童福祉関連の免除額")),
            ],
        ),
        migrations.CreateModel(
            name="AbsenceAccrual",
            fields=[
                (
                    "attendance",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to="attendance.attendance_info",
                        verbose_name="出席記録",
                    ),
                ),
                (
                    "accrual_eligible",
                    models.BooleanField(default=False, verbose_name="加算対象"),
                ),
            ],
        ),
        migrations.AddField(
            model_name="attendance_info",
            name="recipient_number",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="attendance.user",
                verbose_name="受給者番号",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="attendance_info",
            unique_together={("recipient_number", "calendar_date")},
        ),
    ]
