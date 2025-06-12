from django.urls import path

from . import views

app_name = "appointments"

urlpatterns = [
    path("", views.MainView.as_view(), name="main"),
    path(
        "user_appointments",
        views.UserAppointmentsView.as_view(),
        name="user-appointments",
    ),
    path(
        "doctor_appointments",
        views.DoctorAppointmentsView.as_view(),
        name="doctor-appointments",
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
        "appointment/<int:pk>/confirm/",
        views.AppointmentConfirmationView.as_view(),
        name="appointment-confirm",
    ),
    # path(
    #     "appointment/<int:pk>/update/",
    #     views.AppointmentUpdateView.as_view(),
    #     name="appointment-update",
    # ),
    path(
        "appointment/<int:pk>/delete/",
        views.AppointmentDeleteView.as_view(),
        name="appointment-delete",
    ),
    path(
        "appointment/<int:pk>/note/",
        views.AppointmentNoteView.as_view(),
        name="appointment-note",
    ),
    path(
        "appointment/<int:pk>/note/update",
        views.AppointmentNoteUpdateView.as_view(),
        name="appointment-note-update",
    ),
]
