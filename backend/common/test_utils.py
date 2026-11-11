from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User


def create_clinician(email="clinician@example.com", password="StrongPass123!", full_name="Dr. Clinician", specialty="general_medicine", **kwargs):
    return User.objects.create_user(
        email=email, password=password, full_name=full_name,
        role=User.Role.CLINICIAN, specialty=specialty, **kwargs,
    )


def create_patient_user(email="patient@example.com", password="StrongPass123!", full_name="Pat Patient", **kwargs):
    return User.objects.create_user(
        email=email, password=password, full_name=full_name,
        role=User.Role.PATIENT, **kwargs,
    )


def auth_client(user) -> APIClient:
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client
