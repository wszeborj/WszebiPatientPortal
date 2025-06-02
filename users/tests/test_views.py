from http import HTTPStatus

from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages import get_messages
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from users.factories import (
    DepartmentFactory,
    DoctorFactory,
    PatientFactory,
    SpecializationFactory,
    UserFactory,
)
from users.models import User


class TestRegisterUserViews(TestCase):
    def setUp(self):
        self.register_url = reverse("users:register")
        self.login_url = reverse("users:login")
        self.complete_doctor_url = reverse("users:complete-doctor-data")

    def test_register_view_valid_POST(self):
        user_data = {
            "username": "test_username",
            "first_name": "test_name",
            "last_name": "test_last_name",
            "email": "test@test.com",
            "password1": "Test.Password",
            "password2": "Test.Password",
            "role": User.Role.PATIENT,
            "phone_number": "123456789",
            "pesel": "90040536989",
            "street": "test_street",
            "city": "test_city",
            "state": "test_state",
            "postal_code": "23-654",
        }

        response = self.client.post(path=self.register_url, data=user_data, follow=True)

        self.assertRedirects(response, self.login_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(User.objects.count(), 1)

        tested_user = User.objects.first()
        self.assertEqual(User.objects.first().username, user_data["username"])
        self.assertEqual(tested_user.first_name, user_data["first_name"])
        self.assertEqual(tested_user.last_name, user_data["last_name"])
        self.assertEqual(tested_user.email, user_data["email"])
        self.assertEqual(tested_user.role, user_data["role"])
        self.assertEqual(tested_user.phone_number, user_data["phone_number"])
        self.assertEqual(tested_user.pesel, user_data["pesel"])
        self.assertEqual(tested_user.street, user_data["street"])
        self.assertEqual(tested_user.city, user_data["city"])
        self.assertEqual(tested_user.state, user_data["state"])
        self.assertEqual(tested_user.postal_code, user_data["postal_code"])
        self.assertFalse(tested_user.is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            "Activation link to your account on WszebiPatientPortal",
        )

    def test_register_view_invalid_POST(self):
        user_data = {
            "username": "test_username",
            "first_name": "test_name",
            "last_name": "test_last_name",
            "email": "test@test.com",
            "password1": "Test.Password",
            "password2": "Test.Password*",
            "role": User.Role.PATIENT,
            "phone_number": "123456789",
            "pesel": "90040536989",
            "street": "test_street",
            "city": "test_city",
            "state": "test_state",
            "postal_code": "23-654",
        }

        response = self.client.post(path=self.register_url, data=user_data, follow=True)

        self.assertTemplateUsed(response, "users/register.html")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

        form = response.context["form"]
        self.assertIn("password2", form.errors)
        self.assertIn("The two password fields didn’t match.", form.errors["password2"])

    def test_activate_view_success_role_patient_GET(self):
        tested_user = UserFactory(role=User.Role.PATIENT, is_active=False)
        uid = urlsafe_base64_encode(force_bytes(tested_user.pk))
        token = default_token_generator.make_token(tested_user)
        activate_url = reverse("users:activate", args=[uid, token])

        response = self.client.get(path=activate_url, args=[uid, token], follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        tested_user.refresh_from_db()
        self.assertTrue(tested_user.is_active)
        self.assertContains(response, "Your account has been activated!")

    def test_activate_view_success_role_doctor_GET(self):
        tested_user = UserFactory(role=User.Role.DOCTOR, is_active=False)
        uid = urlsafe_base64_encode(force_bytes(tested_user.pk))
        token = default_token_generator.make_token(tested_user)
        activate_url = reverse("users:activate", args=[uid, token])
        response = self.client.get(path=activate_url, args=[uid, token], follow=True)

        messages_list = list(get_messages(response.wsgi_request))
        expected_message = "Your account has been activated, but you still need to complete and confirm your doctor's details."
        self.assertIn(expected_message, str(messages_list[0]))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        tested_user.refresh_from_db()
        self.assertTrue(tested_user.is_active)

    # def test_activate_view_failure_GET(self):
    #     uid = "invalid_uid"
    #     token = "invalid_token"
    #     activate_url = reverse("users:activate", args=[uid, token])
    #
    #     response = self.client.get(path=activate_url, args=[uid, token], follow=True)
    #
    #     self.assertContains(response, "Activation link is invalid!")
    #     self.assertEqual(response.status_code, HTTPStatus.OK)


class TestCompleteDoctorDataViews(TestCase):
    def setUp(self):
        self.complete_doctor_url = reverse("users:complete-doctor-data")

        self.tested_user = UserFactory.create(is_active=True, role=User.Role.DOCTOR)
        self.specialization = SpecializationFactory.create()

        self.client.force_login(self.tested_user)

    def test_complete_doctor_data_post(self):
        doctor_data = {
            "title": "Dr.",
            "description": "Experienced doctor with 10 years of practice",
            "specialization": self.specialization.pk,
        }

        self.client.force_login(self.tested_user)
        response = self.client.post(self.complete_doctor_url, doctor_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("users:login"))
        self.assertEqual(self.tested_user.doctor_profile.title, doctor_data["title"])
        self.assertEqual(
            self.tested_user.doctor_profile.description, doctor_data["description"]
        )
        self.assertEqual(
            self.tested_user.doctor_profile.specialization.first().id,
            doctor_data["specialization"],
        )


class TestDoctorListViews(TestCase):
    def setUp(self):
        self.doctor_list_url = reverse("users:doctor-list")

    def test_doctor_list_view(self):
        DoctorFactory.create_batch(10)
        response = self.client.get(self.doctor_list_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "users/doctor_list.html")
        self.assertEqual(10, len(response.context["doctors"]))

    def test_doctor_list_view_excludes_unconfirmed_doctors(self):
        DoctorFactory.create(confirmed=False)
        response = self.client.get(self.doctor_list_url)
        self.assertEqual(0, len(response.context["doctors"]))


class TestDoctorDetailsViews(TestCase):
    def setUp(self):
        self.tested_doctor = DoctorFactory.create()
        self.doctor_details_url = reverse(
            "users:doctor-details", args=[self.tested_doctor.pk]
        )

    def test_doctor_details_view(self):
        response = self.client.get(self.doctor_details_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/doctor_details.html")
        self.assertEqual(response.context["doctor"], self.tested_doctor)


class TestDepartmentListViews(TestCase):
    def setUp(self):
        self.department_list_url = reverse("users:department-list")

    def test_department_list_view(self):
        DepartmentFactory.create_batch(10)
        response = self.client.get(self.department_list_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "users/department_list.html")
        self.assertEqual(10, len(response.context["departments"]))


# class TestSpecializationListViews(TestCase):
#     def setUp(self):
#         self.department_list_url = reverse("users:doctor-list")


class TestCustomLoginView(TestCase):
    def setUp(self):
        self.custom_login_url = reverse("users:login")

    def test_custom_login_as_doctor(self):
        password = "password123"
        doctor = DoctorFactory.create()

        response = self.client.post(
            self.custom_login_url,
            data={"username": doctor.user.username, "password": password},
            follow=False,
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("appointments:doctor-appointments"))

    def test_custom_login_as_patient(self):
        password = "password123"
        patient = PatientFactory.create()

        response = self.client.post(
            self.custom_login_url,
            data={"username": patient.user.username, "password": password},
            follow=False,
        )
        self.assertRedirects(response, reverse("appointments:user-appointments"))

    def test_anonymous_user_gets_login_page(self):
        response = self.client.post(self.custom_login_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "users/login.html")
