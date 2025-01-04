from django.utils.timezone import now
from django.views.generic import ListView, TemplateView

from appointments.models import Appointment


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
