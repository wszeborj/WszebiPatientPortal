from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic import CreateView, ListView, TemplateView

from appointments.models import Appointment

from .forms import ScheduleDayForm
from .models import ScheduleDay


# Create your views here.
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
            return redirect("appointments:create-schedule-day")

    def form_invalid(self, form):
        print(self.request.POST)
        print(form.errors)
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Błąd w polu {field}: {error}")
        return super().form_invalid(form)
