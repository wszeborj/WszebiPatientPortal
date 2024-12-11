from django.db import models

class Patient(models.Model):
    phone_number = models.CharField(max_length=11, unique=True, help_text="Patient's phone number")
    pesel = models.CharField(max_length=11, unique=True, help_text="Patient's pesel")
    street = models.CharField(max_length=50, help_text="Patient's street of residence")
    city = models.CharField(max_length=50, help_text="Patient's city of residence")
    state = models.CharField(max_length=50, help_text="Patient's state of residence")
    postal_code = models.CharField(max_length=6, help_text="Patient's postal code")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Time when the patient was created.")
    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

class Specialization(models.Model):
    name = models.CharField(max_length=100, help_text="Specialization name")
    description = models.TextField(blank=True, help_text="Details about the specialization")
from django.db import models

class Patient(models.Model):
    first_name = models.CharField(max_length=50, help_text="Patient's first name")
    last_name = models.CharField(max_length=50, help_text="Patient's last name")
    phone_number = models.CharField(max_length=11, unique=True, help_text="Patient's phone number")
    pesel = models.CharField(max_length=11, unique=True, help_text="Patient's pesel")
    street = models.CharField(max_length=50, help_text="Patient's street of residence")
    city = models.CharField(max_length=50, help_text="Patient's city of residence")
    state = models.CharField(max_length=50, help_text="Patient's state of residence")
    postal_code = models.CharField(max_length=6, help_text="Patient's postal code")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Time when the patient was created.")
    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

class Specialization(models.Model):
    name = models.CharField(max_length=100, help_text="Specialization name")
    description = models.TextField(blank=True, help_text="Details about the specialization")

    def __str__(self) -> str:
        return f"{self.name}"

class Doctor(models.Model):
    title = models.CharField(max_length=50, help_text="Doctor's title (e.g., Dr, Prof.)")
    first_name = models.CharField(max_length=50, help_text="Doctor's first name")
    last_name = models.CharField(max_length=50, help_text="Doctor's last name")
    specialization = models.ManyToManyField(
        Specialization,
        related_name="doctors",
        help_text="Specializations of the doctor",)
    phone_number = models.CharField(max_length=11, unique=True, help_text="Doctor's phone number")
    description = models.TextField(blank=True, help_text="Additional details about the doctor")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Time when the doctor was created")

    def __str__(self):
        return f"{self.title} {self.first_name} {self.last_name}"

class Doctor(models.Model):
    title = models.CharField(max_length=50, help_text="Doctor's title (e.g., Dr, Prof.)")
    first_name = models.CharField(max_length=50, help_text="Doctor's first name")
    last_name = models.CharField(max_length=50, help_text="Doctor's last name")
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=11, unique=True, help_text="Doctor's phone number")
    description = models.TextField(blank=True, help_text="Additional details about the doctor")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Time when the doctor was created")

    def __str__(self):
        return f"{self.title} {self.first_name} {self.last_name}"

class DoctorSchedule(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="schedules")
    work_date = models.DateField(help_text="Specific date when the doctor is available")
    start_time = models.TimeField(help_text="Start time for this schedule")
    end_time = models.TimeField(help_text="End time for this schedule")
    interval = models.TimeField(help_text="Time for one patient")
    in_work = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True, help_text="Time when the doctor's schedule was created")

