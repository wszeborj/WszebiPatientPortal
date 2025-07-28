import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import DetailView, FormView, ListView, View

from .forms import DoctorRegistrationForm, UserRegistrationForm
from .models import Department, Doctor, Specialization, User
from .services.perm_assign import assign_user_to_permission_group

logger = logging.getLogger(__name__)

# from django.contrib.auth.mixins import PermissionRequiredMixin


class RegisterUserFormView(FormView):
    template_name = "users/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        UserProcessing.send_user_activation_mail(request=self.request, user=user)

        messages.success(
            self.request,
            f"Dear {user.username}, activate your account by clicking in activation link in sent mail",
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning("FORM ERRORS:", form.errors)
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Issue in field {field}: {error}")
        return super().form_invalid(form)


class CompleteDoctorDataView(LoginRequiredMixin, FormView):
    template_name = "users/register.html"
    form_class = DoctorRegistrationForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        doctor = form.save(commit=False)
        doctor.user = self.request.user
        doctor.save()
        form.save_m2m()
        messages.success(self.request, "Fulfilled data as a doctor!")

        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning("FORM ERRORS:", form.errors)
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error in field {field}: {error}")
        return super().form_invalid(form)


class DoctorListView(ListView):
    template_name = "users/doctor_list.html"
    model = Doctor
    context_object_name = "doctors"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(confirmed=True)
        queryset = queryset.select_related("user").order_by("user__last_name")
        return queryset


class DoctorDetailsView(DetailView):
    template_name = "users/doctor_details.html"
    model = Doctor
    context_object_name = "doctor"


class DepartmentListView(ListView):
    model = Department
    template_name = "users/department_list.html"
    context_object_name = "departments"
    ordering = "name"

    def get_queryset(self):
        return Department.objects.prefetch_related("specializations").all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        departments_with_specializations = {}

        for department in self.get_queryset():
            departments_with_specializations[
                department
            ] = department.specializations.all()

        context["departments_with_specializations"] = departments_with_specializations
        return context


class SpecializationDetailsView(DetailView):
    template_name = "users/specialization_details.html"
    model = Specialization
    context_object_name = "specialization"


class ActivateView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(
            user=user, token=token
        ):
            user.is_active = True
            assign_user_to_permission_group(user)
            user.save()

            if user.role == User.Role.DOCTOR:
                messages.success(
                    request,
                    "Your account has been activated,"
                    " but you still need to complete and confirm your doctor's details.",
                )
                print("redirect")
                return redirect("users:complete-doctor-data")

            messages.success(request, "Your account has been activated!")

            return redirect("users:login")
        else:
            messages.error(request, "Activation link is invalid!")
            return redirect("users:register")


class CustomLoginView(LoginView):
    template_name = "users/login.html"

    def get_success_url(self):
        user = self.request.user
        if user.role == User.Role.PATIENT:
            return reverse_lazy("appointments:user-appointments")
        elif user.role == User.Role.DOCTOR:
            return reverse_lazy("appointments:doctor-appointments")
        else:
            return reverse_lazy("appointments:main")


class UserProcessing:
    @staticmethod
    def send_user_activation_mail(request, user):
        current_site = get_current_site(request)
        subject = "Activation link to your account on WszebiPatientPortal"
        message = render_to_string(
            template_name="users/user_activation_email.html",
            context={
                "user": user,
                "domain": current_site,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
            },
        )
        recipient_mail = user.email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_mail],
            fail_silently=False,
        )

    @staticmethod
    def confirmation_doctor_profile(request, user):
        current_site = get_current_site(request)
        subject = "Confirmation link to your doctor profile"
        message = render_to_string(
            template_name="users/user_activation_email.html",
            context={
                "user": user,
                "domain": current_site,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
            },
        )
        recipient_mail = user.email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_mail],
            fail_silently=False,
        )
