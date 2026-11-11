import importlib

from django.apps import apps as django_apps
from django.test import TestCase

from apps.accounts.models import User
from apps.patients.models import Patient
from apps.visits.models import Visit, VisitSummary


class SeedDataTests(TestCase):
    """The data migration (0002_seed_demo_data) runs automatically while
    building the test database, exactly as it would on a fresh
    `manage.py migrate` - these assertions double as a regression check on
    that migration."""

    def test_demo_clinician_exists_with_usable_password(self):
        clinician = User.objects.get(email="clinician@example.com")
        self.assertEqual(clinician.role, User.Role.CLINICIAN)
        self.assertEqual(clinician.specialty, "general_medicine")
        self.assertTrue(clinician.check_password("demo12345"))

    def test_demo_patient_login_exists_with_usable_password(self):
        patient_user = User.objects.get(email="patient@example.com")
        self.assertEqual(patient_user.role, User.Role.PATIENT)
        self.assertTrue(patient_user.check_password("demo12345"))

    def test_patient_login_linked_to_patient_record(self):
        patient_user = User.objects.get(email="patient@example.com")
        self.assertTrue(Patient.objects.filter(user=patient_user).exists())

    def test_patient_count(self):
        self.assertGreaterEqual(Patient.objects.count(), 3)
        self.assertLessEqual(Patient.objects.count(), 4)

    def test_visit_count(self):
        self.assertGreaterEqual(Visit.objects.count(), 12)
        self.assertLessEqual(Visit.objects.count(), 15)

    def test_all_visits_belong_to_demo_clinician(self):
        clinician = User.objects.get(email="clinician@example.com")
        self.assertEqual(Visit.objects.exclude(clinician=clinician).count(), 0)

    def test_most_visits_have_a_generated_summary(self):
        total = Visit.objects.count()
        with_summary = VisitSummary.objects.count()
        self.assertGreater(with_summary, 0)
        self.assertGreater(with_summary, total / 2)

    def test_at_least_one_visit_without_summary_yet(self):
        # Demonstrates the "not yet generated" state is representable.
        without_summary = Visit.objects.filter(summary__isnull=True).count()
        self.assertGreaterEqual(without_summary, 1)

    def test_seed_summaries_are_non_empty_text(self):
        for summary in VisitSummary.objects.all():
            self.assertTrue(len(summary.patient_friendly_summary.strip()) > 0)

    def test_migration_is_idempotent_on_rerun(self):
        seed_module = importlib.import_module("apps.visits.migrations.0002_seed_demo_data")
        patients_before = Patient.objects.count()
        visits_before = Visit.objects.count()
        summaries_before = VisitSummary.objects.count()

        seed_module.seed_demo_data(django_apps, None)

        self.assertEqual(Patient.objects.count(), patients_before)
        self.assertEqual(Visit.objects.count(), visits_before)
        self.assertEqual(VisitSummary.objects.count(), summaries_before)
