from django.contrib import messages
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
            f"Drogi {user.username}, aktywuj swoje konto klikając w link wysłany na Twojego maila",
        )
        return super().form_valid(form)


class CompleteDoctorDataView(FormView):
    template_name = "users/register.html"
    form_class = DoctorRegistrationForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        doctor = form.save(commit=False)
        doctor.user = self.request.user
        doctor.save()
        form.save_m2m()
        messages.success(self.request, "Uzupełniłeś dane jako lekarz!")

        return super().form_valid(form)


class DoctorListView(ListView):
    template_name = "users/doctor_list.html"
    model = Doctor
    context_object_name = "doctors"
    queryset = Doctor.objects.select_related("user").order_by("user__last_name")


class DoctorDetailsView(DetailView):
    template_name = "users/doctor_details.html"
    model = Doctor
    context_object_name = "doctor"


class DepartmentListView(ListView):
    model = Department
    template_name = "users/department_list.html"
    context_object_name = "departments"
    ordering = "name"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        departments_with_specializations = {}

        for department in Department.objects.all():
            departments_with_specializations[
                department
            ] = department.specializations.all().order_by("name")

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
            user.save()

            if user.role == User.Role.DOCTOR:
                messages.success(
                    request,
                    "Twoje konto zostało aktywowane, "
                    "ale musisz jeszcze usupełnić i potwierdzić dane lekarza",
                )
                return redirect("users:complete-doctor-data")

            messages.success(request, "Twoje konto zostało aktywowane!")
            return redirect("users:login")
        else:
            messages.warning(request, "Link aktywacyjny jest nieprawidłowy!")
            return redirect("users:register")


class CustomLoginView(LoginView):
    template_name = "users/login.html"

    def get_success_url(self):
        user = self.request.user
        if user.role == User.Role.PATIENT:
            return reverse_lazy("appointments:user_appointments")
        elif user.role == User.Role.DOCTOR:
            return reverse_lazy("appointments:doctor_appointments")
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
            from_email="no_reply@wszebipatientportal.pl",
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
            from_email="no_reply@wszebipatientportal.pl",
            recipient_list=[recipient_mail],
            fail_silently=False,
        )
