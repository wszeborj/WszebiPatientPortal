from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.RegisterUserFormView.as_view(), name="register"),
    path(
        "complete-doctor-data/",
        views.CompleteDoctorDataView.as_view(),
        name="complete-doctor-data",
    ),
    path(
        "doctors/",
        views.DoctorListView.as_view(),
        name="doctor-list",
    ),
    path(
        "doctor/<int:pk>",
        views.DoctorDetailsView.as_view(),
        name="doctor-details",
    ),
    path(
        "departments/",
        views.DepartmentListView.as_view(),
        name="department-list",
    ),
    path(
        "specialization/<int:pk>",
        views.SpecializationDetailsView.as_view(),
        name="specialization-details",
    ),
    path("activate/<uidb64>/<token>", views.ActivateView.as_view(), name="activate"),
    path(
        "login/",
        views.CustomLoginView.as_view(),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="users/logout.html"),
        name="logout",
    ),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="users/password_reset.html",
            success_url=reverse_lazy("users:password_reset_done"),
            email_template_name="users/password_reset_email.html",
        ),
        name="password_reset",
    ),
    path(
        "password_reset_done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password_reset_confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            success_url=reverse_lazy("users:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "password_reset_complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]
