from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Doctor, Patient, Specialization, User


class UserRegistrationForm(UserCreationForm):
    ROLE_CHOICES = (
        ("patient", "Patient"),
        ("doctor", "Doctor"),
    )

    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, initial="patient")

    class Meta:
        model = User
        fields = [
            "role",
            "first_name",
            "last_name",
            "username",
            "email",
            "pesel",
            "phone_number",
            "street",
            "city",
            "state",
            "postal_code",
            "avatar",
            "password1",
            "password2",
        ]

    def clean_pesel(self):
        pesel = self.cleaned_data.get("pesel")
        if not pesel.isdigit() or len(pesel) != 11:
            raise forms.ValidationError("PESEL must be exactly 11 digits.")
        if User.objects.filter(pesel=pesel).exists():
            raise forms.ValidationError("PESEL already exists in database.")
        return pesel

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if not phone_number.isdigit() or len(phone_number) != 9:
            raise forms.ValidationError("Phone number must be exactly 9 digits.")
        return phone_number


class PatientRegistrationForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = []


class DoctorRegistrationForm(forms.ModelForm):
    specialization = forms.ModelMultipleChoiceField(
        queryset=Specialization.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text="Select doctor specializations",
    )

    class Meta:
        model = Doctor
        fields = ["title", "specialization", "description"]
