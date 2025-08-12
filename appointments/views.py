import logging
from datetime import date, datetime, timedelta
from typing import Tuple

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)
from django_filters.views import FilterView

from users.models import Department, Doctor

from .filters import DoctorFilter
from .forms import AppointmentForm, AppointmentNoteForm
from .models import Appointment
from .services.doctor_schedule import DoctorScheduleService
from .services.email_utils import (
    send_appointment_confirmed_email,
    send_appointment_created_email,
    send_appointment_deleted_email,
    send_note_added_email,
)

logger = logging.getLogger(__name__)


class MainView(TemplateView):
    template_name = "appointments/main.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        doctors = Doctor.objects.all().prefetch_related("user")
        context["doctors"] = doctors

        departments = Department.objects.all()
        context["departments"] = departments

        return context


class UserAppointmentsView(LoginRequiredMixin, ListView):
    template_name = "appointments/user_appointments.html"
    model = Appointment
    context_object_name = "appointments"
    permission_required = "appointments.view_appointment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        now_time = timezone.now().time()
        user = self.request.user

        common_qs = Appointment.objects.select_related("doctor__user").filter(
            user=user.patient_profile,
        )

        upcoming_appointment = common_qs.filter(
            Q(date__gt=today) | Q(date=today, time__gte=now_time)
        ).order_by("date", "time")

        past_appointment = common_qs.filter(
            Q(date__lt=today) | Q(date=today, time__lt=now_time)
        ).order_by("date", "time")

        context["upcoming_appointment"], context["past_appointment"] = (
            upcoming_appointment,
            past_appointment,
        )
        return context


class DoctorAppointmentsView(PermissionRequiredMixin, ListView):
    template_name = "appointments/doctor_appointments.html"
    model = Appointment
    context_object_name = "appointments"
    permission_required = "appointments.view_appointment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        now_time = timezone.now().time()
        user = self.request.user

        common_qs = Appointment.objects.select_related("user__user").filter(
            doctor=user.doctor_profile,
        )
        upcoming_appointment = common_qs.filter(
            Q(date__gt=today) | Q(date=today, time__gte=now_time),
        )

        past_appointment = common_qs.filter(
            Q(date__lt=today) | Q(date=today, time__lt=now_time),
        )

        context["upcoming_appointment"] = upcoming_appointment.order_by("date", "time")
        context["past_appointment"] = past_appointment.order_by("date", "time")

        return context


class AppointmentListView(ListView, FilterView):
    model = Doctor
    template_name = "appointments/appointment_list.html"
    context_object_name = "appointments"
    filterset_class = DoctorFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_week_param(self) -> Tuple[date, date, str, str]:
        week_param = self.request.GET.get("week")

        if week_param:
            start_of_week = datetime.strptime(week_param, "%Y-%m-%d").date()
        else:
            today = datetime.today().date()
            start_of_week = today - timedelta(days=today.weekday())

        previous_week = (start_of_week - timedelta(days=7)).strftime("%Y-%m-%d")
        next_week = (start_of_week + timedelta(days=7)).strftime("%Y-%m-%d")
        end_of_week = start_of_week + timedelta(days=6)

        return start_of_week, end_of_week, previous_week, next_week

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        start_of_week, end_of_week, previous_week, next_week = self.get_week_param()

        all_doctors = self.get_queryset().select_related("user")

        doctor_week_schedule = DoctorScheduleService.get_doctor_schedule_week(
            start_of_week, end_of_week, all_doctors
        )

        context["previous_week"] = previous_week
        context["next_week"] = next_week
        context["start_of_week"] = start_of_week
        context["end_of_week"] = end_of_week

        context["doctor_week_schedule"] = doctor_week_schedule
        context["filter"] = self.filterset
        return context


class AppointmentCreateView(PermissionRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = "appointments/appointment_form.html"
    permission_required = "appointments.add_appointment"

    def form_valid(self, form):
        appointment = form.save(commit=False)
        appointment.user = self.request.user.patient_profile
        appointment.save()
        self.object = appointment
        send_appointment_created_email(appointment)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy(
            "appointments:appointment-confirm", kwargs={"pk": self.object.pk}
        )

    def form_invalid(self, form):
        logger.error(f"FORM ERRORS: {form.errors}")
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Issue in field {field}: {error}")
        return super().form_invalid(form)


class AppointmentConfirmationView(PermissionRequiredMixin, View):
    permission_required = "appointments.add_appointment"
    template_name = "appointments/appointment_confirm.html"

    def get_appointment(self, pk, request):
        return get_object_or_404(Appointment, pk=pk, user=request.user.patient_profile)

    def get(self, request, pk, *args, **kwargs):
        appointment = self.get_appointment(pk, request)
        return render(request, self.template_name, {"appointment": appointment})

    def post(self, request, pk, *args, **kwargs):
        appointment = self.get_appointment(pk, request)
        appointment.is_confirmed = True
        appointment.save()
        messages.success(request, "Appointment confirmed.")
        send_appointment_confirmed_email(appointment)
        return redirect("appointments:appointments-list")


class AppointmentDeleteView(PermissionRequiredMixin, DeleteView):
    model = Appointment
    template_name = "appointments/appointment_confirm_delete.html"
    # success_url = reverse_lazy("appointments:appointments-list")
    permission_required = "appointments.delete_appointment"

    def form_valid(self, form):
        send_appointment_deleted_email(self.object)
        return super().form_valid(form)

    def get_success_url(self):
        user = self.request.user
        if hasattr(user, "doctor_profile"):
            return reverse_lazy("appointments:doctor-appointments")
        elif hasattr(user, "patient_profile"):
            return reverse_lazy("appointments:user-appointments")
        return reverse_lazy("appointments:appointments-list")


class AppointmentNoteView(PermissionRequiredMixin, DetailView):
    model = Appointment
    template_name = "appointments/appointment_note_detail.html"
    context_object_name = "appointment"
    permission_required = "appointments.view_appointment"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if hasattr(user, "patient_profile"):
            return queryset.filter(user=user.patient_profile)
        elif hasattr(user, "doctor_profile"):
            return queryset.filter(doctor=user.doctor_profile)

        return queryset.none()


class AppointmentNoteUpdateView(PermissionRequiredMixin, UpdateView):
    model = Appointment
    form_class = AppointmentNoteForm
    template_name = "appointments/appointment_note_form.html"
    permission_required = "appointments.change_appointment"

    def get_success_url(self):
        send_note_added_email(self.object)
        return reverse_lazy("appointments:doctor-appointments")
