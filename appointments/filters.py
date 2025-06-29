import django_filters
from django import forms
from django.db.models import Q

from users.models import Doctor, Specialization


def get_doctor_title_choices():
    choices = []
    for title in Doctor.objects.values_list("title", flat=True).distinct():
        choices.append((title, title))
    return choices


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
        choices=get_doctor_title_choices,
        label="Doctor title",
    )
    # doctor_title = django_filters.ChoiceFilter(choices=get_doctor_title_choices)

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
