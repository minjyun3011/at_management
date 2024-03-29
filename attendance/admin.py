from django.contrib import admin
from .models import Attendance, Kid_Information, Event


admin.site.register(Attendance)
admin.site.register(Kid_Information)

class EventAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'end_time', 'full_name', 'gender')  # 管理サイトで表示するフィールド
    list_filter = ('gender',)  # フィルタリングに使用するフィールド

# admin.site.register()の呼び出しに、カスタマイズした管理クラスを追加
admin.site.register(Event, EventAdmin)
