from rest_framework import serializers

from apps.accounts.models import User
from apps.patients.models import Patient


class PatientSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Patient
        fields = ["id", "full_name", "date_of_birth", "mrn", "user", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_user(self, value):
        if value is not None and not value.is_patient_role:
            raise serializers.ValidationError("Linked user must have role='patient'.")
        return value
