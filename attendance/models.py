from django.db import models
from django.utils import timezone
from django.utils.text import slugify

# 保護者用画面
class Attendance(models.Model):
    ATTENDANCE_CHOICES = [
        (1, '出席'),
        (2, '欠席'),
    ]
    choice = models.IntegerField('出欠予定',choices=ATTENDANCE_CHOICES, default=1 )
    created_at = models.DateTimeField('最新更新日時', default=timezone.now)

    def __str__(self):
        # 出欠状況のラベルを取得するための辞書を作成
        attendance_dict = dict(self.ATTENDANCE_CHOICES)
        # 出席状況のラベルを取得し、name と組み合わせた文字列を返します。
        return f"({attendance_dict.get(self.choice)})"
    

class Kid_Information(models.Model):
    slug = models.SlugField('登録番号', max_length=6, unique=True)
    first_name = models.CharField('名', max_length=20)
    family_name = models.CharField('姓', max_length=20)
    email = models.EmailField('メールアドレス', blank=True)
    attendance = models.ForeignKey(
            Attendance, verbose_name='本日の出欠予定', on_delete=models.PROTECT
        )
    created_at = models.DateTimeField('作成日時', default=timezone.now)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    # この関数でデータのIDから登録番号(6桁)に表示し直す
    def save(self, *args, **kwargs):
        if not self.slug:
            # ここで最後の登録番号を取得して1増やすなどのロジックを実装
            # 例として、モデルのインスタンス数を基にしていますが、
            # 実際にはより複雑なロジックが必要になるかもしれません。
            last_number = Kid_Information.objects.count()
            next_number = last_number + 1
            # ゼロ埋めされた形式でslugを設定
            self.slug = slugify(f'{next_number:06d}')
        super(Kid_Information, self).save(*args, **kwargs)

    def __str__(self):
        return '{0} {1} {2} {3} {4} {5}'.format(self.slug, self.family_name, self.first_name, self.email, self.attendance, self.updated_at )
