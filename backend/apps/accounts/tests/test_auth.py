from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from common.test_utils import auth_client, create_clinician, create_patient_user


class RegistrationTests(APITestCase):
    def test_clinician_registration(self):
        url = reverse("auth-register")
        response = self.client.post(url, {
            "email": "newclinician@example.com",
            "password": "StrongPass123!",
            "full_name": "Dr. New Clinician",
            "role": "clinician",
            "specialty": "cardiology",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        user = User.objects.get(email="newclinician@example.com")
        self.assertEqual(user.role, User.Role.CLINICIAN)
        self.assertEqual(user.specialty, "cardiology")

    def test_patient_registration_ignores_specialty(self):
        url = reverse("auth-register")
        response = self.client.post(url, {
            "email": "newpatient@example.com",
            "password": "StrongPass123!",
            "full_name": "New Patient",
            "role": "patient",
            "specialty": "should-be-ignored",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        user = User.objects.get(email="newpatient@example.com")
        self.assertEqual(user.role, User.Role.PATIENT)
        self.assertIsNone(user.specialty)

    def test_duplicate_email_rejected(self):
        create_patient_user(email="dupe@example.com")
        url = reverse("auth-register")
        response = self.client.post(url, {
            "email": "dupe@example.com",
            "password": "StrongPass123!",
            "full_name": "Dupe",
            "role": "patient",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_weak_password_rejected(self):
        url = reverse("auth-register")
        response = self.client.post(url, {
            "email": "weak@example.com",
            "password": "123",
            "full_name": "Weak",
            "role": "patient",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginAndMeTests(APITestCase):
    def setUp(self):
        self.clinician = create_clinician(email="c1@example.com", password="StrongPass123!")

    def test_login_returns_tokens_with_role_claim(self):
        url = reverse("auth-login")
        response = self.client.post(url, {"email": "c1@example.com", "password": "StrongPass123!"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_wrong_password_rejected(self):
        url = reverse("auth-login")
        response = self.client.post(url, {"email": "c1@example.com", "password": "WrongPass!"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_endpoint_returns_profile(self):
        client = auth_client(self.clinician)
        response = client.get(reverse("users-me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role"], "clinician")
        self.assertEqual(response.data["email"], "c1@example.com")

    def test_me_requires_authentication(self):
        response = self.client.get(reverse("users-me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_patch_updates_full_name(self):
        client = auth_client(self.clinician)
        response = client.patch(reverse("users-me"), {"full_name": "Dr. Updated Name"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.clinician.refresh_from_db()
        self.assertEqual(self.clinician.full_name, "Dr. Updated Name")

    def test_logout_blacklists_refresh_token(self):
        login_response = self.client.post(reverse("auth-login"), {"email": "c1@example.com", "password": "StrongPass123!"})
        refresh = login_response.data["refresh"]
        client = auth_client(self.clinician)
        logout_response = client.post(reverse("auth-logout"), {"refresh": refresh})
        self.assertEqual(logout_response.status_code, status.HTTP_205_RESET_CONTENT)

        refresh_response = self.client.post(reverse("auth-refresh"), {"refresh": refresh})
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_rotates_token(self):
        login_response = self.client.post(reverse("auth-login"), {"email": "c1@example.com", "password": "StrongPass123!"})
        old_refresh = login_response.data["refresh"]
        refresh_response = self.client.post(reverse("auth-refresh"), {"refresh": old_refresh})
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)
        self.assertIn("refresh", refresh_response.data)
        self.assertNotEqual(refresh_response.data["refresh"], old_refresh)

        # Old refresh token is blacklisted after rotation and can't be reused.
        reuse_response = self.client.post(reverse("auth-refresh"), {"refresh": old_refresh})
        self.assertEqual(reuse_response.status_code, status.HTTP_401_UNAUTHORIZED)
