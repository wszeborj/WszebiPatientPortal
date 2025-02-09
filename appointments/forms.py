from django import forms

from .models import Appointment


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = []

    def __init__(self, *args, **kwargs):
        doctor = kwargs.pop("doctor", None)
        date = kwargs.pop("date", None)
        time = kwargs.pop("time", None)
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if doctor and date and time and user:
            self.instance.doctor = doctor
            self.instance.date = date
            self.instance.time = time
            self.instance.user = user

    def clean(self):
        cleaned_data = super().clean()
        self._validate_no_overlap(cleaned_data)

    def _validate_no_overlap(self, cleaned_data):
        work_date = cleaned_data.get("date")
        start_time = cleaned_data.get("time")
        doctor = cleaned_data.get("doctor")

        overlapping_appointments = Appointment.objects.filter(
            doctor=doctor, date=work_date, time=start_time
        )

        if overlapping_appointments.exists():
            raise forms.ValidationError(
                "The specified appointment overlaps with an existing one. Please choose another one."
            )
