from django.test import TestCase

from users.factories import UserFactory
from users.forms import UserRegistrationForm


class TestUserRegistrationForm(TestCase):
    def test_valid_form(self):
        data = {
            "role": "patient",
            "first_name": "Anna",
            "last_name": "Nowak",
            "username": "anna123",
            "email": "anna@example.com",
            "pesel": "12345678901",
            "phone_number": "123456789",
            "street": "ul. Leśna",
            "city": "Warszawa",
            "state": "mazowieckie",
            "postal_code": "00-001",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        }
        form = UserRegistrationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_pesel_format(self):
        user = UserFactory.build(pesel="badpesel", phone_number="123456789")
        data = user.__dict__
        form = UserRegistrationForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("pesel", form.errors)

    def test_duplicate_pesel(self):
        UserFactory(pesel="11111111111")
        user = UserFactory.build(pesel="11111111111")
        data = user.__dict__
        form = UserRegistrationForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("pesel", form.errors)

    def test_invalid_phone_number(self):
        user = UserFactory.build(phone_number="abc123")
        data = user.__dict__
        form = UserRegistrationForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)
