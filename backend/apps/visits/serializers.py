from rest_framework import serializers

from apps.patients.models import Patient
from apps.visits.models import Visit, VisitSummary


class VisitSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitSummary
        fields = ["id", "visit", "patient_friendly_summary", "generated_at"]
        read_only_fields = fields


class VisitSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    patient_name = serializers.CharField(source="patient.full_name", read_only=True)
    patient_mrn = serializers.CharField(source="patient.mrn", read_only=True)
    clinician_name = serializers.CharField(source="clinician.full_name", read_only=True)
    has_summary = serializers.SerializerMethodField()

    class Meta:
        model = Visit
        fields = [
            "id", "patient", "patient_name", "patient_mrn", "clinician", "clinician_name",
            "visit_date", "chief_complaint", "clinical_notes", "diagnosis", "treatment_plan",
            "created_at", "has_summary",
        ]
        read_only_fields = ["id", "clinician", "created_at"]

    def get_has_summary(self, obj) -> bool:
        return hasattr(obj, "summary")
