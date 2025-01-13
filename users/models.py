from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        PATIENT = "patient", "Patient"
        DOCTOR = "doctor", "Doctor"

    role = models.CharField(
        max_length=20, choices=Role.choices, help_text="Role of the user"
    )
    phone_number = models.CharField(
        max_length=9, unique=True, help_text="Patient's phone number"
    )
    pesel = models.CharField(max_length=11, unique=True, help_text="Patient's pesel")
    street = models.CharField(max_length=50, help_text="Patient's street of residence")
    city = models.CharField(max_length=50, help_text="Patient's city of residence")
    state = models.CharField(max_length=50, help_text="Patient's state of residence")
    postal_code = models.CharField(max_length=6, help_text="Patient's postal code")
    avatar = models.ImageField(
        upload_to="avatar of user",
        help_text="Image of user's avatar.",
        max_length=255,
        blank=True,
    )


class Patient(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="patient_profile"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Time when the patient was created."
    )
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Specialization(models.Model):
    name = models.CharField(max_length=100, help_text="Specialization name")
    description = models.TextField(
        blank=True, help_text="Details about the specialization"
    )

    def __str__(self) -> str:
        return f"{self.name}"


class Doctor(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="doctor_profile"
    )
    title = models.CharField(
        max_length=50, help_text="Doctor's title (e.g., Dr, Prof.)"
    )
    specialization = models.ManyToManyField(
        Specialization,
        related_name="doctors",
        help_text="Specializations of the doctor",
    )
    description = models.TextField(
        blank=True, help_text="Additional details about the doctor"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Time when the patient was created."
    )
    modified_at = models.DateTimeField(auto_now=True)
    confirmed = models.BooleanField(
        default=False, help_text="Whether the doctor is confirmed."
    )

    def __str__(self):
        return f"{self.title} {self.first_name} {self.last_name}"
