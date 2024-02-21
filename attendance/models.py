from django.db import models
from django.utils import timezone

# Create your models here.
class Kid_Information(models.Model):
    ATTENDANCE_CHOICES = [
        (1, '出席'),
        (2, '欠席'),
    ]

    name = models.CharField('名前', max_length=20)
    attendance = models.IntegerField('出欠状況',choices=ATTENDANCE_CHOICES, default=1 )
    created_at = models.DateTimeField('更新日時', default=timezone.now)

    def __str__(self):
        # 出欠状況のラベルを取得するための辞書を作成
        attendance_dict = dict(self.ATTENDANCE_CHOICES)
        # 出席状況のラベルを取得し、name と組み合わせた文字列を返します。
        return f"{self.name} ({attendance_dict.get(self.attendance)})"
