from django.contrib import admin
from .models import User, Attendance_info, AbsenceAccrual, ServiceTime

#Admin管理サイトにモデル新規登録
admin.site.register(User)
admin.site.register(Attendance_info)
admin.site.register(AbsenceAccrual)

@admin.register(ServiceTime)
class ServiceTimeAdmin(admin.ModelAdmin):
    list_display = ['weekday', 'service_type', 'start_time', 'end_time']
