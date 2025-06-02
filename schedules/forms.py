from datetime import date, datetime, time, timedelta

from bootstrap_datepicker_plus.widgets import DatePickerInput
from django import forms

from .models import ScheduleDay


def validate_interval(interval):
    if interval % 5 != 0:
        raise forms.ValidationError(
            "The appointment duration must be a multiple of 5 minutes."
        )
    if interval < 5 or interval > 60:
        raise forms.ValidationError(
            "The appointment duration must be between 5 and 60 minutes."
        )


class ScheduleDayForm(forms.ModelForm):
    work_date = forms.DateField(
        label="Work Date",
        widget=DatePickerInput(options={"format": "YYYY/MM/DD"}),
        help_text="Enter the date in the format: YYYY-MM-DD",
    )
    start_time = forms.TimeField(
        label="Start Time",
        widget=forms.TimeInput(attrs={"type": "time", "step": "300"}),
        help_text="Enter the start time in the format: HH:MM",
    )
    end_time = forms.TimeField(
        label="End Time",
        widget=forms.TimeInput(attrs={"type": "time", "step": "300"}),
        help_text="Enter the end time in the format: HH:MM",
    )
    interval = forms.IntegerField(
        label="Appointment Duration (minutes)",
        widget=forms.NumberInput(
            attrs={"placeholder": "e.g., 15", "step": 5, "min": 5, "max": 60}
        ),
        help_text="Enter the interval in minutes (e.g., 15 for 15 minutes)",
        validators=[validate_interval],
    )

    class Meta:
        model = ScheduleDay
        fields = ["work_date", "start_time", "end_time", "interval"]

    def __init__(self, *args, **kwargs):
        self.doctor = kwargs.pop("doctor", None)
        super().__init__(*args, **kwargs)
        self._set_default_values()

    def _set_default_values(self):
        today = date.today()
        default_start_time = time(8, 0)
        default_end_time = time(14, 0)
        default_interval = 15

        last_schedule = (
            ScheduleDay.objects.filter(doctor=self.doctor)
            .order_by("modified_at")
            .last()
        )
        if last_schedule:
            self.fields["work_date"].initial = last_schedule.work_date
            self.fields["start_time"].initial = last_schedule.start_time
            self.fields["end_time"].initial = last_schedule.end_time
            self.fields["interval"].initial = int(
                last_schedule.interval.total_seconds() / 60
            )
        else:
            self.fields["work_date"].initial = today
            self.fields["start_time"].initial = default_start_time
            self.fields["end_time"].initial = default_end_time
            self.fields["interval"].initial = default_interval

    def clean_interval(self):
        interval = self.cleaned_data["interval"]
        return timedelta(minutes=interval)

    def clean(self):
        cleaned_data = super().clean()
        self._validate_required_fields(cleaned_data)
        self._validate_time_range(cleaned_data)
        self._validate_no_overlap(cleaned_data)
        return cleaned_data

    def _validate_required_fields(self, cleaned_data):
        for field in self.Meta.fields:
            if not cleaned_data.get(field):
                raise forms.ValidationError(f"The field '{field}' must be filled out.")

    def _validate_time_range(self, cleaned_data):
        work_date = cleaned_data.get("work_date")
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        interval = cleaned_data.get("interval")

        start_datetime = datetime.combine(work_date, start_time)
        end_datetime = datetime.combine(work_date, end_time)

        if start_datetime > end_datetime:
            raise forms.ValidationError("End time is before start time.")

        duration = end_datetime - start_datetime
        if interval > duration:
            raise forms.ValidationError(
                "The interval is longer than the specified time range."
            )

        if duration % interval != timedelta(0):
            suggested_end_time = (
                start_datetime + (duration // interval) * interval
            ).time()
            raise forms.ValidationError(
                f"The interval does not fit within the specified time range. Suggested end time: {suggested_end_time}."
            )

    def _validate_no_overlap(self, cleaned_data):
        work_date = cleaned_data.get("work_date")
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        overlapping_schedules = ScheduleDay.objects.filter(
            doctor=self.doctor,
            work_date=work_date,
            start_time__lte=end_time,
            end_time__gte=start_time,
        )

        if overlapping_schedules.exists():
            raise forms.ValidationError(
                "The specified schedule overlaps with an existing one. Please adjust the hours."
            )
