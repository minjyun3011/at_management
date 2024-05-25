from django.urls import path
from .views import input
from .views.input import HomePageView, CheckUserView, UserRegistrationView, Home1View

app_name = "attendance"


urlpatterns = [
    path('', HomePageView.as_view(), name='home'),  # 初期登録またはログインページ
    path('check_user/', CheckUserView.as_view(), name='check_user'),  # 受給者番号でのログインを処理
    path('register/', UserRegistrationView.as_view(), name='register'),  # 新規ユーザー登録処理
    path('home1/', Home1View.as_view(), name='home1'),  # General access without user ID
    path('api/get_events/', input.get_events, name='get_events'), #カレンダー初期化時の処理
    path('api/add_event/',input.add_event, name='add_event' ), #出欠情報新規登録時の処理
    path('api/get_event_details/', input.get_event_details, name='get_event_details'),
    path('api/edit_event/', input.edit_event, name='edit_event'),

]

