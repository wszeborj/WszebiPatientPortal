from datetime import date, datetime, timedelta
from typing import Tuple

import django_filters
from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

# from django.db.models import DateTimeField, ExpressionWrapper, F
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)
from django_filters.views import FilterView

from users.models import Department, Doctor, Specialization

from .forms import AppointmentForm, AppointmentNoteForm
from .models import Appointment
from .services.date_parser import try_parsing_date
from .services.doctor_schedule import DoctorScheduleService
from .services.email_utils import (
    send_appointment_created_email,
    send_appointment_deleted_email,
    send_note_added_email,
)


class MainView(TemplateView):
    template_name = "appointments/main.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        doctors_amount = Doctor.objects.count()
        context[doctors_amount] = doctors_amount

        departments = Department.objects.all()
        context["departments"] = departments

        return context


class UserAppointmentsView(ListView):
    template_name = "appointments/user_appointments.html"
    model = Appointment
    context_object_name = "appointments"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     now_datetime = timezone.now()
    #     user = self.request.user
    #
    #     appointments_with_datetime = self.model.objects.annotate(
    #         full_datetime=ExpressionWrapper(
    #             F("date") + F("time"),
    #             output_field=DateTimeField()
    #         )
    #     )
    #
    #     upcoming_appointment = appointments_with_datetime.filter(
    #         user=user.patient_profile,
    #         full_datetime__gte=now_datetime
    #     ).order_by("full_datetime")
    #
    #     past_appointment = appointments_with_datetime.filter(
    #         user=user.patient_profile,
    #         full_datetime__lt=now_datetime
    #     ).order_by("-full_datetime")
    #
    #     context["upcoming_appointment"] = upcoming_appointment
    #     context["past_appointment"] = past_appointment
    #     return context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        now_time = timezone.now().time()
        user = self.request.user

        upcoming_appointment = Appointment.objects.filter(
            Q(date__gt=today) | Q(date=today, time__gte=now_time),
            user=user.patient_profile,
        )

        past_appointment = Appointment.objects.filter(
            Q(date__lt=today) | Q(date=today, time__lt=now_time),
            user=user.patient_profile,
        )

        context["upcoming_appointment"] = upcoming_appointment.order_by("date", "time")
        context["past_appointment"] = past_appointment.order_by("date", "time")
        return context


class DoctorAppointmentsView(ListView):
    template_name = "appointments/doctor_appointments.html"
    model = Appointment
    context_object_name = "appointments"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    # now_datetime = timezone.now()
    # user = self.request.user
    #
    # appointments_with_datetime = self.model.objects.annotate(
    #     full_datetime=ExpressionWrapper(
    #         F("date") + F("time"),
    #         output_field=DateTimeField()
    #     )
    # )
    #
    # upcoming_appointment = appointments_with_datetime.filter(
    #     doctor=user.doctor_profile,
    #     full_datetime__gte=now_datetime
    # ).order_by("full_datetime")
    #
    # past_appointment = appointments_with_datetime.filter(
    #     doctor=user.doctor_profile,
    #     full_datetime__lt=now_datetime
    # ).order_by("-full_datetime")
    #
    # context["upcoming_appointment"] = upcoming_appointment
    # context["past_appointment"] = past_appointment
    #
    # return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        now_time = timezone.now().time()
        user = self.request.user

        upcoming_appointment = Appointment.objects.filter(
            Q(date__gt=today) | Q(date=today, time__gte=now_time),
            doctor=user.doctor_profile,
        )

        past_appointment = Appointment.objects.filter(
            Q(date__lt=today) | Q(date=today, time__lt=now_time),
            doctor=user.doctor_profile,
        )

        context["upcoming_appointment"] = upcoming_appointment.order_by("date", "time")
        context["past_appointment"] = past_appointment.order_by("date", "time")

        return context


class DoctorFilter(django_filters.FilterSet):
    doctor_id = django_filters.NumberFilter(
        field_name="id", label="", widget=forms.HiddenInput()
    )
    specialization = django_filters.ModelMultipleChoiceFilter(
        queryset=Specialization.objects.all().order_by("name"), label="Specialization"
    )

    doctor_name = django_filters.CharFilter(
        method="filter_doctor_name", label="First name and second name"
    )

    doctor_title = django_filters.ChoiceFilter(
        field_name="title",
        choices=[
            (title, title)
            for title in Doctor.objects.values_list("title", flat=True).distinct()
        ],
        label="Doctor title",
    )

    def filter_doctor_name(self, queryset, name, value):
        parts = value.split()

        query = Q()
        for part in parts:
            query |= Q(user__first_name__icontains=part) | Q(
                user__last_name__icontains=part
            )

        return queryset.filter(query)

    class Meta:
        model = Doctor
        fields = ["doctor_title", "doctor_name", "specialization"]


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

        all_doctors = self.get_queryset()

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


class AppointmentCreateView(LoginRequiredMixin, CreateView):
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
        date = try_parsing_date(date_str)
        time = datetime.strptime(time_str, "%H:%M").time()

        kwargs["doctor"] = doctor
        kwargs["date"] = date
        kwargs["time"] = time
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        send_appointment_created_email(self.object)
        return super().form_valid(form)

    def form_invalid(self, form):
        # print(self.request.POST)
        # print(form.errors)
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Issue in field {field}: {error}")
        return super().form_invalid(form)


# class AppointmentUpdateView(LoginRequiredMixin, UpdateView):
#     model = Appointment
#     form_class = AppointmentForm
#     template_name = "appointments/appointment_form.html"
#     success_url = reverse_lazy("appointments:appointments-list")


class AppointmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Appointment
    template_name = "appointments/appointment_confirm_delete.html"
    success_url = reverse_lazy("appointments:appointments-list")

    def form_valid(self, form):
        response = super().form_valid(form)
        send_appointment_deleted_email(self.object)
        return response


class AppointmentNoteView(LoginRequiredMixin, DetailView):
    model = Appointment
    template_name = "appointments/appointment_note_detail.html"
    context_object_name = "appointment"

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "patient_profile"):
            return Appointment.objects.filter(user=user.patient_profile)
        elif hasattr(user, "doctor_profile"):
            return Appointment.objects.filter(doctor=user.doctor_profile)


class AppointmentNoteUpdateView(UpdateView):
    model = Appointment
    form_class = AppointmentNoteForm
    template_name = "appointments/appointment_note_form.html"

    def get_success_url(self):
        send_note_added_email(self.object)
        return reverse_lazy("appointments:doctor-appointments")
