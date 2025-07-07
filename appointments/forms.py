from django import forms

from schedules.models import ScheduleDay

from .models import Appointment


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["doctor", "date", "time"]
        widgets = {
            "doctor": forms.HiddenInput(),
            "date": forms.HiddenInput(),
            "time": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        self._validate_no_overlap(cleaned_data)

    def _validate_no_overlap(self, cleaned_data):
        work_date = cleaned_data.get("date")
        start_time = cleaned_data.get("time")
        doctor = cleaned_data.get("doctor")

        if not all([doctor, work_date, start_time]):
            raise forms.ValidationError("Missing data.")

        schedule_query = ScheduleDay.objects.filter(
            doctor=doctor,
            work_date=work_date,
            start_time__lte=start_time,
            end_time__gt=start_time,
        )
        if not schedule_query.exists():
            raise forms.ValidationError(
                "The doctor is not available at the selected date and time."
            )

        overlapping_appointments = Appointment.objects.filter(
            doctor=doctor,
            date=work_date,
            time=start_time,
        )
        if self.instance.pk:
            overlapping_appointments = overlapping_appointments.exclude(
                pk=self.instance.pk
            )

        if overlapping_appointments.exists():
            raise forms.ValidationError(
                "The specified appointment overlaps with an existing one. Please choose another one."
            )


class AppointmentNoteForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 10, "class": "form-control"}),
        }
