from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView

from .forms import ScheduleDayForm
from .models import ScheduleDay


class ScheduleCalendarView(TemplateView):
    template_name = "schedules/schedule_calendar.html"

    def get_context_data(self, **kwargs):
        doctor = self.request.user.doctor_profile
        schedule_days = ScheduleDay.objects.filter(doctor=doctor)
        context = super().get_context_data(**kwargs)
        context["schedule_days"] = schedule_days
        return context


class ScheduleDayCreateView(CreateView):
    model = ScheduleDay
    template_name = "schedules/schedule_form.html"
    form_class = ScheduleDayForm
    success_url = reverse_lazy("schedules:schedule-calendar")

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
            return redirect("schedules:schedule-calendar")
        elif action == "save":
            messages.success(
                self.request, "Grafik został zapisany! Możesz dodać kolejny dzień."
            )
            return redirect("schedules:schedule-day-create")

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Błąd w polu {field}: {error}")
        return super().form_invalid(form)


class ScheduleDayUpdateView(UpdateView):
    template_name = "schedules/schedule_form.html"
    form_class = ScheduleDayForm
    model = ScheduleDay
    success_url = reverse_lazy("schedules:schedule-calendar")


class ScheduleDayDeleteView(DeleteView):
    template_name = "schedules/schedule_confirm_delete.html"
    model = ScheduleDay
    success_url = reverse_lazy("schedules:schedule-calendar")
