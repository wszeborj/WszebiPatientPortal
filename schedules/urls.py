from django.urls import path

from . import views

app_name = "schedules"

urlpatterns = [
    path(
        "schedule_calendar/",
        views.ScheduleCalendarView.as_view(),
        name="schedule-calendar",
    ),
    path(
        "create_scheduleday/",
        views.ScheduleDayCreateView.as_view(),
        name="schedule-day-create",
    ),
    path(
        "scheduleday/<int:pk>/update/",
        views.ScheduleDayUpdateView.as_view(),
        name="schedule-day-update",
    ),
    path(
        "scheduleday/<int:pk>/delete/",
        views.ScheduleDayDeleteView.as_view(),
        name="schedule-day-delete",
    ),
    path(
        "schedule_calendar/",
        views.ScheduleCalendarView.as_view(),
        name="schedule-calendar",
    ),
]
