from django.conf import settings
from django.db import models


class Visit(models.Model):
    """One clinical visit. Owned by the clinician who recorded it - a
    clinician's visit queryset is always scoped to `clinician=request.user`
    (see views.py), so another clinician's visit 404s rather than 403s."""

    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE, related_name="visits")
    clinician = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="visits")
    visit_date = models.DateField()
    chief_complaint = models.TextField()
    clinical_notes = models.TextField()
    diagnosis = models.TextField()
    treatment_plan = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-visit_date", "-created_at"]
        indexes = [models.Index(fields=["clinician", "visit_date"])]

    def __str__(self):
        return f"Visit(patient={self.patient_id}, date={self.visit_date})"


class VisitSummary(models.Model):
    """The AI-generated, patient-friendly translation of a Visit. One per
    visit; regenerating replaces `patient_friendly_summary` and bumps
    `generated_at` rather than creating a second row - see
    apps/visits/views.py `generate_summary`."""

    visit = models.OneToOneField(Visit, on_delete=models.CASCADE, related_name="summary")
    patient_friendly_summary = models.TextField()
    generated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"VisitSummary(visit={self.visit_id})"
