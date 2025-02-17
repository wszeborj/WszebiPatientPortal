from datetime import date, datetime, timedelta
from typing import Tuple

from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)

from users.models import Doctor

from .forms import AppointmentForm
from .models import Appointment
from .services.doctor_schedule import DoctorScheduleService


class MainView(TemplateView):
    template_name = "appointments/main.html"


class UserAppointmentsView(ListView):
    template_name = "appointments/user_appointments.html"
    model = Appointment
    context_object_name = "appointments"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now_datetime = timezone.now()

        upcoming_appointment = self.model.objects.filter(
            date__gte=now_datetime.date(), time__gte=now_datetime.time()
        ).order_by("date", "time")
        past_appointment = self.model.objects.filter(
            date__lte=now_datetime.date(), time__lte=now_datetime.time()
        ).order_by("-date", "-time")

        context["upcoming_appointment"] = upcoming_appointment
        context["past_appointment"] = past_appointment
        return context


class AppointmentListView(ListView):
    model = Appointment
    template_name = "appointments/appointment_list.html"
    context_object_name = "appointments"

    def get_week_param(self) -> Tuple[date, date, str, str]:
        week_param = self.request.GET.get("week")

        if week_param:
            start_of_week = datetime.strptime(week_param, "%Y-%m-%d")
        else:
            today = datetime.today()
            start_of_week = today - timedelta(days=today.weekday())

        previous_week = (start_of_week - timedelta(days=7)).strftime("%Y-%m-%d")
        next_week = (start_of_week + timedelta(days=7)).strftime("%Y-%m-%d")
        end_of_week = start_of_week + timedelta(days=6)

        return start_of_week, end_of_week, previous_week, next_week

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        start_of_week, end_of_week, previous_week, next_week = self.get_week_param()

        doctor_week_schedule = DoctorScheduleService.get_doctor_schedule_week(
            start_of_week, end_of_week
        )

        context["previous_week"] = previous_week
        context["next_week"] = next_week
        context["start_of_week"] = start_of_week
        context["end_of_week"] = end_of_week

        context["doctor_week_schedule"] = doctor_week_schedule

        return context


class AppointmentCreateView(CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = "appointments/appointment_form.html"
    success_url = reverse_lazy("appointments:appointments-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        doctor_id = self.request.GET.get("doctor")
        date_str = self.request.GET.get("date")
        time_str = self.request.GET.get("time")

        doctor = get_object_or_404(Doctor, id=doctor_id)
        date = datetime.strptime(date_str, "%b. %d, %Y").date()
        time = datetime.strptime(time_str, "%H:%M").time()

        kwargs["doctor"] = doctor
        kwargs["date"] = date
        kwargs["time"] = time
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        # print(self.request.POST)
        # print(form.errors)
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Issue in field {field}: {error}")
        return super().form_invalid(form)


class AppointmentUpdateView(UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = "appointments/appointment_form.html"
    success_url = reverse_lazy("appointments:appointments-list")


class AppointmentDeleteView(DeleteView):
    model = Appointment
    template_name = "appointments/appointment_confirm_delete.html"
    success_url = reverse_lazy("appointments:appointments-list")
