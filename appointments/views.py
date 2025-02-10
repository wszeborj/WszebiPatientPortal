from datetime import datetime, timedelta

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

from schedules.models import ScheduleDay
from users.models import Doctor

from .forms import AppointmentForm
from .models import Appointment


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        week_param = self.request.GET.get("week")

        if week_param:
            start_of_week = datetime.strptime(week_param, "%Y-%m-%d")
        else:
            today = datetime.today()
            start_of_week = today - timedelta(days=today.weekday())

        previous_week = (start_of_week - timedelta(days=7)).strftime("%Y-%m-%d")
        next_week = (start_of_week + timedelta(days=7)).strftime("%Y-%m-%d")
        end_of_week = start_of_week + timedelta(days=6)
        context["previous_week"] = previous_week
        context["next_week"] = next_week
        context["start_of_week"] = start_of_week
        context["end_of_week"] = end_of_week
        context["week_days"] = list(range(7))

        all_doctors = Doctor.objects.all()

        doctor_week_schedule = {}
        for doctor in all_doctors:
            schedule_days = ScheduleDay.objects.filter(
                doctor=doctor, work_date__range=[start_of_week, end_of_week]
            )
            doctor_schedule_day = {}
            for schedule_day in schedule_days:
                available_slots = []
                current_time = datetime.combine(
                    schedule_day.work_date, schedule_day.start_time
                )
                end_time = datetime.combine(
                    schedule_day.work_date, schedule_day.end_time
                )
                while current_time < end_time:
                    is_past = current_time < datetime.now()
                    is_taken = Appointment.objects.filter(
                        doctor=schedule_day.doctor,
                        date=schedule_day.work_date,
                        time=current_time.time(),
                    ).exists()
                    slot = {
                        "time": current_time.strftime("%H:%M"),
                        "is_taken": is_taken,
                        "is_past": is_past,
                    }
                    available_slots.append(slot)
                    current_time += schedule_day.interval

                doctor_schedule_day[schedule_day.work_date] = available_slots

            for day_num in range(7):
                date_time = start_of_week + timedelta(days=day_num)
                date = date_time.date()
                if date not in doctor_schedule_day.keys():
                    doctor_schedule_day[date] = []

            doctor_schedule_day = dict(sorted(doctor_schedule_day.items()))
            doctor_week_schedule[doctor] = doctor_schedule_day

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
