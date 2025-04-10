from django.db import models


class ScheduleDay(models.Model):
    doctor = models.ForeignKey(
        "users.Doctor", on_delete=models.CASCADE, related_name="schedule"
    )
    work_date = models.DateField(help_text="Specific date when the doctor is available")
    start_time = models.TimeField(help_text="Start time for this schedule")
    end_time = models.TimeField(help_text="End time for this schedule")
    interval = models.DurationField(help_text="Duration of one appointment slot")
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Time when the doctor's schedule was created"
    )
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["doctor", "work_date", "start_time"]

    def __str__(self):
        return f"{self.work_date} {self.start_time}-{self.end_time}"
