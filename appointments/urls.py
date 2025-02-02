from django.urls import path

from . import views

app_name = "appointments"

urlpatterns = [
    path("", views.MainView.as_view(), name="main"),
    path(
        "user_appointments",
        views.UserAppointmentsView.as_view(),
        name="user_appointments",
    ),
    path(
        "schedule_calendar/",
        views.ScheduleCalendarView.as_view(),
        name="schedule-calendar",
    ),
    path(
        "create_scheduleday/",
        views.ScheduleDayCreateView.as_view(),
        name="create-schedule-day",
    ),
]
