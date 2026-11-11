from django.conf import settings
from django.db import models


class Patient(models.Model):
    """A patient record maintained by clinicians. Optionally linked to a
    patient-role User via a nullable one-to-one, so a patient can
    eventually log in and see their own visit summaries - kept as a simple
    nullable link rather than a full patient-portal self-registration/
    linking flow, which is out of scope for this build."""

    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    mrn = models.CharField(max_length=32, unique=True, verbose_name="MRN")
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patient_record",
        help_text="Optional link to this patient's own login, once they have one.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name} (MRN {self.mrn})"
