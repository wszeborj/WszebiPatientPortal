from .models import User
from django.shortcuts import redirect
from django.urls import reverse

class CompleteDoctorProfileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        excluded_paths = [
            reverse("users:logout"),
            reverse("users:complete-doctor-data"),
        ]
        if request.user.is_authenticated:
            if request.path not in excluded_paths:
                if (request.user.role == User.Role.DOCTOR and
                    not hasattr(request.user, "doctor_profile")):
                    return redirect("users:complete-doctor-data")

        response = self.get_response(request)

        return response