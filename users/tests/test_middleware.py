from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse

from users.factories import DoctorFactory, UserFactory
from users.middleware import CompleteDoctorProfileMiddleware
from users.models import User


class TestCompleteDoctorProfileMiddleware(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.get_response = lambda request: HttpResponse("OK")
        self.middleware = CompleteDoctorProfileMiddleware(self.get_response)

    def test_redirects_doctor_without_profile(self):
        user = UserFactory(role=User.Role.DOCTOR)
        request = self.factory.get("schedules:schedule-calendar")
        request.user = user

        response = self.middleware(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("users:complete-doctor-data"))

    def test_allows_doctor_with_profile(self):
        user = UserFactory(role=User.Role.DOCTOR)
        DoctorFactory(user=user)
        request = self.factory.get("schedules:schedule-calendar")
        request.user = user

        response = self.middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")

    def test_skips_if_path_is_excluded(self):
        user = UserFactory(role=User.Role.DOCTOR)
        request = self.factory.get(reverse("users:complete-doctor-data"))
        request.user = user

        response = self.middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")

    def test_skips_for_authenticated_non_doctor(self):
        user = UserFactory(role=User.Role.PATIENT)
        request = self.factory.get("schedules:schedule-calendar")
        request.user = user

        response = self.middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")

    def test_skips_for_unauthenticated_user(self):
        request = self.factory.get("schedules:schedule-calendar")
        request.user = self._get_unauthenticated_user()

        response = self.middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")

    def _get_unauthenticated_user(self):
        class DummyUser:
            is_authenticated = False

        return DummyUser()
