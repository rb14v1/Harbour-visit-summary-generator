from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.common.ai import generate_visit_summary
from apps.patients.models import Patient
from apps.visits.models import Visit, VisitSummary
from common.test_utils import auth_client, create_clinician


class GenerateSummaryTests(APITestCase):
    def setUp(self):
        self.clinician = create_clinician(email="summarydoc@example.com")
        self.client_auth = auth_client(self.clinician)
        self.patient = Patient.objects.create(full_name="Kara Example", date_of_birth="1991-03-03", mrn="MRN-3001")
        self.visit = Visit.objects.create(
            patient=self.patient, clinician=self.clinician,
            visit_date="2026-03-01",
            chief_complaint="Productive cough and chest congestion for 5 days.",
            clinical_notes="Rx: amoxicillin 500mg TID x7d for acute bacterial sinusitis.",
            diagnosis="Acute bacterial sinusitis.",
            treatment_plan="Amoxicillin 500mg three times daily for 7 days, increase fluid intake.",
        )

    def test_generate_summary_creates_summary(self):
        response = self.client_auth.post(reverse("visit-generate-summary", args=[self.visit.id]))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(VisitSummary.objects.filter(visit=self.visit).exists())
        self.assertTrue(len(response.data["patient_friendly_summary"]) > 0)

    def test_generate_summary_requires_ownership(self):
        other_clinician = create_clinician(email="notmine@example.com")
        other_client = auth_client(other_clinician)
        response = other_client.post(reverse("visit-generate-summary", args=[self.visit.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_regenerate_replaces_rather_than_duplicates(self):
        first = self.client_auth.post(reverse("visit-generate-summary", args=[self.visit.id]))
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(VisitSummary.objects.filter(visit=self.visit).count(), 1)

        # Change the underlying visit so the regenerated text would differ
        # from a fresh create if a second row were (incorrectly) made.
        self.visit.treatment_plan = "Switched to azithromycin due to penicillin allergy."
        self.visit.save()

        second = self.client_auth.post(reverse("visit-generate-summary", args=[self.visit.id]))
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(VisitSummary.objects.filter(visit=self.visit).count(), 1)

        summary = VisitSummary.objects.get(visit=self.visit)
        self.assertEqual(summary.id, first.data["id"])
        self.assertIn("azithromycin", summary.patient_friendly_summary)

    def test_stub_summary_is_deterministic_across_calls(self):
        first_text = generate_visit_summary(
            chief_complaint=self.visit.chief_complaint,
            clinical_notes=self.visit.clinical_notes,
            diagnosis=self.visit.diagnosis,
            treatment_plan=self.visit.treatment_plan,
        )
        second_text = generate_visit_summary(
            chief_complaint=self.visit.chief_complaint,
            clinical_notes=self.visit.clinical_notes,
            diagnosis=self.visit.diagnosis,
            treatment_plan=self.visit.treatment_plan,
        )
        self.assertEqual(first_text, second_text)

    def test_stub_summary_differs_for_different_input(self):
        text_a = generate_visit_summary(
            chief_complaint="Headache.", clinical_notes="n/a",
            diagnosis="Tension headache.", treatment_plan="OTC ibuprofen.",
        )
        text_b = generate_visit_summary(
            chief_complaint="Headache.", clinical_notes="n/a",
            diagnosis="Migraine.", treatment_plan="Sumatriptan as needed.",
        )
        self.assertNotEqual(text_a, text_b)

    def test_generate_summary_via_endpoint_is_deterministic(self):
        response_1 = self.client_auth.post(reverse("visit-generate-summary", args=[self.visit.id]))
        text_1 = response_1.data["patient_friendly_summary"]

        # Regenerate without changing the visit - stub output must match.
        response_2 = self.client_auth.post(reverse("visit-generate-summary", args=[self.visit.id]))
        text_2 = response_2.data["patient_friendly_summary"]
        self.assertEqual(text_1, text_2)


class FetchSummaryTests(APITestCase):
    def setUp(self):
        self.clinician = create_clinician(email="fetchdoc@example.com")
        self.client_auth = auth_client(self.clinician)
        self.patient = Patient.objects.create(full_name="Leo Example", date_of_birth="1983-12-12", mrn="MRN-4001")
        self.visit = Visit.objects.create(
            patient=self.patient, clinician=self.clinician,
            visit_date="2026-03-05",
            chief_complaint="Annual physical.",
            clinical_notes="Unremarkable exam.",
            diagnosis="Routine health maintenance.",
            treatment_plan="Continue current lifestyle, return in one year.",
        )

    def test_summary_404_before_generation(self):
        response = self.client_auth.get(reverse("visit-summary", args=[self.visit.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_summary_200_after_generation(self):
        self.client_auth.post(reverse("visit-generate-summary", args=[self.visit.id]))
        response = self.client_auth.get(reverse("visit-summary", args=[self.visit.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("patient_friendly_summary", response.data)

    def test_fetch_summary_requires_ownership(self):
        self.client_auth.post(reverse("visit-generate-summary", args=[self.visit.id]))
        other_clinician = create_clinician(email="notmine2@example.com")
        other_client = auth_client(other_clinician)
        response = other_client.get(reverse("visit-summary", args=[self.visit.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
