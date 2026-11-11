from rest_framework import permissions, viewsets

from apps.common.permissions import IsClinician
from apps.patients.models import Patient
from apps.patients.serializers import PatientSerializer


class PatientViewSet(viewsets.ModelViewSet):
    """Full CRUD on patient records, clinician-only. Every authenticated
    clinician can manage every patient record (patient records are a
    shared clinic roster, not per-clinician data - unlike Visit, which is
    scoped to the clinician who created it)."""

    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsClinician]
    filterset_fields = ["mrn"]
