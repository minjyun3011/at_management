from django.urls import path, include
from . import views
from .views import HomePageView, CheckUserView, UserRegistrationView, Home1View
# Attendance_TodayView


app_name = "attendance"


urlpatterns = [
    path('', HomePageView.as_view(), name='home'),  # 初期登録またはログインページ
    path('check_user/', CheckUserView.as_view(), name='check_user'),  # 受給者番号でのログインを処理
    path('register/', UserRegistrationView.as_view(), name='register'),  # 新規ユーザー登録処理
    path('home1/', Home1View.as_view(), name='home1'),  # General access without user ID
    # path('home1/<int:user_id>/', Home1View.as_view(), name='home1'),
    path('api/get_events/', views.get_events, name='get_events'),
    path('api/add_event/',views.add_event, name='add_event' ),
    # path('attendance/<int:pk>/', Attendance_TodayView.as_view(), name='attendance-detail'),  # 特定ユーザーの詳細情報表示（必要に応じて有効化）
]
