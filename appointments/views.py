from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import AppointmentForm, ScheduleDayForm
from .models import Appointment, ScheduleDay


class MainView(TemplateView):
    template_name = "appointments/main.html"


class UserAppointmentsView(ListView):
    template_name = "appointments/user_appointments.html"
    model = Appointment
    context_object_name = "appointments"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now_datetime = now()

        upcoming_appointment = self.model.objects.filter(
            date__gte=now_datetime.date(), time__gte=now_datetime.time()
        ).order_by("date", "time")
        past_appointment = self.model.objects.filter(
            date__lte=now_datetime.date(), time__lte=now_datetime.time()
        ).order_by("-date", "-time")

        context["upcoming_appointment"] = upcoming_appointment
        context["past_appointment"] = past_appointment
        return context


class ScheduleCalendarView(TemplateView):
    template_name = "appointments/schedule_calendar.html"

    def get_context_data(self, **kwargs):
        doctor = self.request.user.doctor_profile
        schedule_days = ScheduleDay.objects.filter(doctor=doctor)
        context = super().get_context_data(**kwargs)
        context["schedule_days"] = schedule_days
        return context


class ScheduleDayCreateView(CreateView):
    model = ScheduleDay
    template_name = "appointments/schedule_form.html"
    form_class = ScheduleDayForm
    success_url = reverse_lazy("appointments:schedule-calendar")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["doctor"] = self.request.user.doctor_profile
        return kwargs

    def form_valid(self, form):
        action = self.request.POST.get("action")
        doctor = self.request.user.doctor_profile
        schedule = form.save(commit=False)
        schedule.doctor = doctor
        schedule.save()
        if action == "save_exit":
            messages.success(self.request, "Grafik został zapisany!.")
            return super().form_valid(form)
        elif action == "save":
            messages.success(
                self.request, "Grafik został zapisany! Możesz dodać kolejny dzień."
            )
            return redirect("appointments:schedule-day-create")

    def form_invalid(self, form):
        # print(self.request.POST)
        # print(form.errors)
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Błąd w polu {field}: {error}")
        return super().form_invalid(form)


class ScheduleDayUpdateView(UpdateView):
    template_name = "appointments/schedule_form.html"
    form_class = ScheduleDayForm
    model = ScheduleDay
    success_url = reverse_lazy("appointments:schedule-calendar")


class ScheduleDayDeleteView(DeleteView):
    template_name = "appointments/schedule_confirm_delete.html"
    model = ScheduleDay
    success_url = reverse_lazy("appointments:schedule-calendar")


class AppointmentListView(ListView):
    model = Appointment
    template_name = "appointments/appointment_list.html"
    context_object_name = "appointments"


class AppointmentCreateView(CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = "appointments/appointment_form.html"
    success_url = reverse_lazy("appointments:appointments-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        appointment = form.save(commit=False)
        appointment.user = user
        appointment.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        print(self.request.POST)
        print(form.errors)
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
