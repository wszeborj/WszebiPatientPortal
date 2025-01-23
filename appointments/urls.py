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
    path(
        "appointments/",
        views.AppointmentListView.as_view(),
        name="appointments-list",
    ),
    path(
        "create_appointment/",
        views.AppointmentCreateView.as_view(),
        name="appointment-create",
    ),
    path(
        "appointment/<int:pk>/update/",
        views.AppointmentUpdateView.as_view(),
        name="appointment-update",
    ),
    path(
        "appointment/<int:pk>/delete/",
        views.AppointmentDeleteView.as_view(),
        name="appointment-delete",
    ),
]
