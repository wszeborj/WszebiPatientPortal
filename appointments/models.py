from django.db import models


class Appointment(models.Model):
    doctor = models.ForeignKey(
        "users.Doctor", on_delete=models.CASCADE, related_name="appointments"
    )
    user = models.ForeignKey(
        "users.Patient",
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    date = models.DateField()
    time = models.TimeField()
    notes = models.TextField(
        blank=True, help_text="Additional notes for the appointment"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_canceled = models.BooleanField(default=False)

    class Meta:
        ordering = ["doctor", "date", "time"]

    def __str__(self):
        return f"Wizyta u {self.doctor} na {self.date} o {self.time}"
