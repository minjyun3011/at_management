from django.urls import path, include
from . import views
from .views import HomePageView, Attendance_TodayView


app_name = "attendance"


urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('attendance/<int:pk>/', Attendance_TodayView.as_view(), name='attendance-detail'),
]
