from django.db import models
import datetime

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

    recipient_number = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name="受給者番号", to_field='recipient_number')
    calendar_date = models.DateField(verbose_name="日付")
    start_time = models.TimeField(verbose_name="開始時間", null=True, blank=True)  # オプションに変更
    end_time = models.TimeField(verbose_name="終了時間", null=True, blank=True)    # オプションに変更
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
        unique_together = ('recipient_number', 'calendar_date')  # recipient_numberと日付の組み合わせはユニーク

    def __str__(self):
        user_name = self.recipient_number.name if self.recipient_number else "Unknown User"
        return f'{user_name} - {self.calendar_date} - {self.status}'

class AbsenceAccrual(models.Model):
    attendance = models.OneToOneField(
        'Attendance_info',
        on_delete=models.CASCADE,
        verbose_name="出席記録",
        primary_key=True
    )
    accrual_eligible = models.BooleanField(default=False, verbose_name="加算対象")

    def __str__(self):
        # Attendance_info から関連する User の名前を取得
        user_name = self.attendance.recipient_number.name if self.attendance and self.attendance.recipient_number else "Unknown User"
        # Attendance_info の日付を取得
        calendar_date = self.attendance.calendar_date if self.attendance else "No Date"
        eligible_status = "Eligible" if self.accrual_eligible else "Not Eligible"
        return f'{user_name} - {calendar_date} - {eligible_status}'

