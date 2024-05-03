from django.contrib import admin
from .models import User, Attendance_info, AbsenceAccrual

#Admin管理サイトにモデル新規登録
admin.site.register(User)
admin.site.register(Attendance_info)
admin.site.register(AbsenceAccrual)

