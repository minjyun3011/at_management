from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.formats import date_format
import datetime
from django.contrib.auth.models import AbstractUser


# 利用者の個人情報テーブル
class User(models.Model):
    class GenderChoices(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'

    class EducationLevelChoices(models.TextChoices):
        KINDERGARTEN_YOUNG = 'KY', '年少'
        KINDERGARTEN_MIDDLE = 'KM', '年中'
        KINDERGARTEN_OLD = 'KO', '年長'
        ELEMENTARY_1 = 'E1', '小学1年'
        ELEMENTARY_2 = 'E2', '小学2年'
        ELEMENTARY_3 = 'E3', '小学3年'
        ELEMENTARY_4 = 'E4', '小学4年'
        ELEMENTARY_5 = 'E5', '小学5年'
        ELEMENTARY_6 = 'E6', '小学6年'

    name = models.CharField(max_length=100, verbose_name="氏名")
    birthdate = models.DateField(verbose_name="生年月日")
    gender = models.CharField(
        max_length=1,
        choices=GenderChoices.choices,
        default=GenderChoices.OTHER,
        verbose_name="性別"
    )
    recipient_number = models.CharField(max_length=20, unique=True, verbose_name="受給者番号", primary_key=True)
    education_level = models.CharField(
        max_length=2,
        choices=EducationLevelChoices.choices,
        default=EducationLevelChoices.KINDERGARTEN_YOUNG,
        verbose_name="教育区分"
    )
    welfare_exemption = models.IntegerField(verbose_name="児童福祉関連の免除額")

    def __str__(self):
        return self.name

    @property
    def age(self):
        today = datetime.date.today()
        return today.year - self.birthdate.year - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))


# 利用者の日ごとの出欠情報テーブル
class Attendance_info(models.Model):
    class AttendanceStatus(models.TextChoices):
        PRESENT = 'PR', '出席'
        ABSENT = 'AB', '欠席'

    class TransportationService(models.TextChoices):
        USED = 'US', '利用'
        NOT_USED = 'NU', '未利用'

    user = models.CharField(verbose_name="利用者", max_length=50)
    recipient_number = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name="受給者番号")
    calendar_date = models.DateField(verbose_name="日付")
    start_time = models.TimeField(verbose_name="開始時間")
    end_time = models.TimeField(verbose_name="終了時間")
    status = models.CharField(
        max_length=2,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT,
        verbose_name="出席状態"
    )
    transportation_to = models.CharField(
        max_length=2,
        choices=TransportationService.choices,
        default=TransportationService.NOT_USED,
        verbose_name="送迎サービス（往路）"
    )
    transportation_from = models.CharField(
        max_length=2,
        choices=TransportationService.choices,
        default=TransportationService.NOT_USED,
        verbose_name="送迎サービス（復路）"
    )
    absence_reason = models.TextField(blank=True, null=True, verbose_name="欠席理由")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        unique_together = ('user', 'calendar_date')  # 利用者と日付の組み合わせはユニーク

    def __str__(self):
        return f'{self.user.name} - {self.calendar_date} - {self.get_status_display()}'


# (職員閲覧用)欠席加算の有無に関するテーブル
class AbsenceAccrual(models.Model):
    attendance = models.OneToOneField(
        'Attendance_info',
        on_delete=models.CASCADE,
        verbose_name="出席記録",
        primary_key=True
    )
    accrual_eligible = models.BooleanField(default=False, verbose_name="加算対象")

    def __str__(self):
        return f'{self.attendance.user.name} - {self.attendance.date} - {"Eligible" if self.accrual_eligible else "Not Eligible"}'

####
    

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
    

class Event(models.Model):
    GENDER_CHOICES = (
        ('M', '男'),
        ('F', '女'),
    )
    start_time = models.DateTimeField()  # イベントの開始時間
    end_time = models.DateTimeField()    # イベントの終了時間
    full_name = models.CharField(max_length=100)  # 参加者のフルネーム
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    calendar_date = models.DateField(null=True)  # カレンダーの日付、nullを許容

    def __str__(self):
        # 性別に基づいて接尾語を決定
        suffix = 'くん' if self.gender == 'M' else 'ちゃん'

        # start_timeとend_timeから時間部分のみをフォーマット
        start_time_str = self.start_time.strftime('%H:%M')if self.start_time else "未定"
        end_time_str = self.end_time.strftime('%H:%M')if self.end_time else "未定"

        # calendar_dateがNoneでない場合のみフォーマットを適用
        calendar_date_str = date_format(self.calendar_date, "SHORT_DATE_FORMAT") if self.calendar_date else "日付未定"

        # フォーマットされた文字列を返す
        return f"{calendar_date_str} {start_time_str}〜{end_time_str} {self.full_name}{suffix}"
