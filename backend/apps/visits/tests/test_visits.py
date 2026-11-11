from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.patients.models import Patient
from apps.visits.models import Visit
from common.test_utils import auth_client, create_clinician, create_patient_user


class VisitCrudTests(APITestCase):
    def setUp(self):
        self.clinician = create_clinician(email="clinA@example.com")
        self.client_auth = auth_client(self.clinician)
        self.patient = Patient.objects.create(full_name="Ivy Example", date_of_birth="1992-09-09", mrn="MRN-1001")

    def _visit_payload(self, **overrides):
        payload = {
            "patient": self.patient.id,
            "visit_date": "2026-01-15",
            "chief_complaint": "Sore throat and fever for 3 days.",
            "clinical_notes": "Temp 101.2F, erythematous pharynx, no exudate.",
            "diagnosis": "Acute viral pharyngitis.",
            "treatment_plan": "Rest, fluids, OTC acetaminophen for fever.",
        }
        payload.update(overrides)
        return payload

    def test_create_visit_sets_clinician_from_request(self):
        response = self.client_auth.post(reverse("visit-list"), self._visit_payload())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        visit = Visit.objects.get(id=response.data["id"])
        self.assertEqual(visit.clinician, self.clinician)

    def test_list_visits_scoped_to_clinician(self):
        Visit.objects.create(patient=self.patient, clinician=self.clinician, **{
            "visit_date": "2026-01-10", "chief_complaint": "x", "clinical_notes": "x",
            "diagnosis": "x", "treatment_plan": "x",
        })
        other_clinician = create_clinician(email="clinB@example.com")
        Visit.objects.create(patient=self.patient, clinician=other_clinician, **{
            "visit_date": "2026-01-11", "chief_complaint": "y", "clinical_notes": "y",
            "diagnosis": "y", "treatment_plan": "y",
        })
        response = self.client_auth.get(reverse("visit-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_retrieve_own_visit(self):
        visit = Visit.objects.create(patient=self.patient, clinician=self.clinician, **{
            "visit_date": "2026-01-10", "chief_complaint": "x", "clinical_notes": "x",
            "diagnosis": "x", "treatment_plan": "x",
        })
        response = self.client_auth.get(reverse("visit-detail", args=[visit.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_own_visit(self):
        visit = Visit.objects.create(patient=self.patient, clinician=self.clinician, **{
            "visit_date": "2026-01-10", "chief_complaint": "x", "clinical_notes": "x",
            "diagnosis": "x", "treatment_plan": "x",
        })
        response = self.client_auth.patch(reverse("visit-detail", args=[visit.id]), {"diagnosis": "Updated diagnosis."})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        visit.refresh_from_db()
        self.assertEqual(visit.diagnosis, "Updated diagnosis.")

    def test_delete_own_visit(self):
        visit = Visit.objects.create(patient=self.patient, clinician=self.clinician, **{
            "visit_date": "2026-01-10", "chief_complaint": "x", "clinical_notes": "x",
            "diagnosis": "x", "treatment_plan": "x",
        })
        response = self.client_auth.delete(reverse("visit-detail", args=[visit.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Visit.objects.filter(id=visit.id).exists())

    def test_patient_role_user_forbidden(self):
        patient_user = create_patient_user(email="patientuser2@example.com")
        client = auth_client(patient_user)
        response = client.get(reverse("visit-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_rejected(self):
        response = self.client.get(reverse("visit-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class VisitCrossClinicianOwnershipTests(APITestCase):
    """Proves clinician B gets 404 (not 403, not leaked data) on clinician
    A's visit - queryset-level scoping, see VisitViewSet.get_queryset."""

    def setUp(self):
        self.patient = Patient.objects.create(full_name="Jack Example", date_of_birth="1988-11-11", mrn="MRN-2001")
        self.clinician_a = create_clinician(email="owner@example.com")
        self.clinician_b = create_clinician(email="other@example.com")
        self.visit = Visit.objects.create(
            patient=self.patient, clinician=self.clinician_a,
            visit_date="2026-02-01", chief_complaint="Back pain.",
            clinical_notes="Tenderness L4-L5.", diagnosis="Lumbar strain.",
            treatment_plan="NSAIDs, physical therapy.",
        )

    def test_other_clinician_gets_404_on_retrieve(self):
        client_b = auth_client(self.clinician_b)
        response = client_b.get(reverse("visit-detail", args=[self.visit.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_other_clinician_gets_404_on_update(self):
        client_b = auth_client(self.clinician_b)
        response = client_b.patch(reverse("visit-detail", args=[self.visit.id]), {"diagnosis": "Hijacked."})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.visit.refresh_from_db()
        self.assertEqual(self.visit.diagnosis, "Lumbar strain.")

    def test_other_clinician_gets_404_on_delete(self):
        client_b = auth_client(self.clinician_b)
        response = client_b.delete(reverse("visit-detail", args=[self.visit.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Visit.objects.filter(id=self.visit.id).exists())

    def test_other_clinician_visit_not_in_list(self):
        client_b = auth_client(self.clinician_b)
        response = client_b.get(reverse("visit-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_owning_clinician_can_still_access(self):
        client_a = auth_client(self.clinician_a)
        response = client_a.get(reverse("visit-detail", args=[self.visit.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
