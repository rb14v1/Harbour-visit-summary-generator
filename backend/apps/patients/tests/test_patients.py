from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.patients.models import Patient
from common.test_utils import auth_client, create_clinician, create_patient_user


class PatientCrudTests(APITestCase):
    def setUp(self):
        self.clinician = create_clinician(email="clin@example.com")
        self.client_auth = auth_client(self.clinician)

    def test_create_patient(self):
        response = self.client_auth.post(reverse("patient-list"), {
            "full_name": "Alice Example",
            "date_of_birth": "1990-01-01",
            "mrn": "MRN-0001",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(Patient.objects.filter(mrn="MRN-0001").exists())

    def test_list_patients(self):
        # Seed-data migration already creates a few demo Patient rows, so
        # assert the delta rather than an absolute count of 1.
        count_before = Patient.objects.count()
        Patient.objects.create(full_name="Bob Example", date_of_birth="1985-05-05", mrn="MRN-0002")
        response = self.client_auth.get(reverse("patient-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], count_before + 1)

    def test_retrieve_patient(self):
        patient = Patient.objects.create(full_name="Carol Example", date_of_birth="1970-02-02", mrn="MRN-0003")
        response = self.client_auth.get(reverse("patient-detail", args=[patient.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["full_name"], "Carol Example")

    def test_update_patient(self):
        patient = Patient.objects.create(full_name="Dan Example", date_of_birth="1960-03-03", mrn="MRN-0004")
        response = self.client_auth.patch(reverse("patient-detail", args=[patient.id]), {"full_name": "Daniel Example"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        patient.refresh_from_db()
        self.assertEqual(patient.full_name, "Daniel Example")

    def test_delete_patient(self):
        patient = Patient.objects.create(full_name="Eve Example", date_of_birth="1980-04-04", mrn="MRN-0005")
        response = self.client_auth.delete(reverse("patient-detail", args=[patient.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Patient.objects.filter(id=patient.id).exists())

    def test_duplicate_mrn_rejected(self):
        Patient.objects.create(full_name="Frank Example", date_of_birth="1975-06-06", mrn="MRN-0006")
        response = self.client_auth.post(reverse("patient-list"), {
            "full_name": "Frank Duplicate",
            "date_of_birth": "1975-06-06",
            "mrn": "MRN-0006",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_link_to_patient_role_user_succeeds(self):
        patient_user = create_patient_user(email="linked@example.com")
        response = self.client_auth.post(reverse("patient-list"), {
            "full_name": "Grace Example",
            "date_of_birth": "1995-07-07",
            "mrn": "MRN-0007",
            "user": patient_user.id,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_link_to_clinician_role_user_rejected(self):
        other_clinician = create_clinician(email="otherclin@example.com")
        response = self.client_auth.post(reverse("patient-list"), {
            "full_name": "Henry Example",
            "date_of_birth": "1965-08-08",
            "mrn": "MRN-0008",
            "user": other_clinician.id,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PatientPermissionTests(APITestCase):
    def test_patient_role_user_forbidden(self):
        patient_user = create_patient_user(email="patientuser@example.com")
        client = auth_client(patient_user)
        response = client.get(reverse("patient-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_rejected(self):
        response = self.client.get(reverse("patient-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
