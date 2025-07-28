import logging

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView

from .forms import ScheduleDayForm
from .models import ScheduleDay

logger = logging.getLogger(__name__)


class ScheduleCalendarView(PermissionRequiredMixin, TemplateView):
    template_name = "schedules/schedule_calendar.html"
    permission_required = (
        "schedules.add_scheduleday",
        "schedules.change_scheduleday",
        "schedules.delete_scheduleday",
        "schedules.view_scheduleday",
    )

    def get_context_data(self, **kwargs):
        user = self.request.user
        if hasattr(user, "doctor_profile"):
            doctor = user.doctor_profile
            schedule_days = ScheduleDay.objects.filter(doctor=doctor)
        elif self.request.user.is_staff:
            schedule_days = ScheduleDay.objects.all()
        else:
            schedule_days = []

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
            messages.success(self.request, "Schedule saved!.")
            return redirect("schedules:schedule-calendar")
        elif action == "save":
            messages.success(self.request, "Schedule saved! You can add another day.")
            return redirect("schedules:schedule-day-create")

    def form_invalid(self, form):
        logger.warning("FORM ERRORS:", form.errors)
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error in field {field}: {error}")
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
