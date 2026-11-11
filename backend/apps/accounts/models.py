from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.accounts.managers import UserManager


class User(AbstractUser):
    class Role(models.TextChoices):
        CLINICIAN = "clinician", "Clinician"
        PATIENT = "patient", "Patient"

    username = None
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True, default="")
    role = models.CharField(max_length=20, choices=Role.choices)

    # Clinician-only, nullable - blank for patient-role users. Free text
    # (e.g. "general_medicine", "cardiology") rather than a fixed choice
    # list, kept deliberately simple for this demo.
    specialty = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"

    @property
    def is_clinician(self):
        return self.role == self.Role.CLINICIAN

    @property
    def is_patient_role(self):
        return self.role == self.Role.PATIENT
