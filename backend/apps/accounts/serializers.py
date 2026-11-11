from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "full_name", "role", "specialty", "date_joined"]
        read_only_fields = ["id", "role", "date_joined"]


class RegisterSerializer(serializers.ModelSerializer):
    """Role-aware self-registration. `specialty` is accepted only for
    clinicians (silently ignored for patients, kept simple rather than
    rejecting an unexpected field)."""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    role = serializers.ChoiceField(choices=User.Role.choices)
    specialty = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = User
        fields = ["id", "email", "password", "full_name", "role", "specialty"]

    def validate(self, attrs):
        if attrs.get("role") != User.Role.CLINICIAN:
            attrs.pop("specialty", None)
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Adds `role` to the JWT claims.

    The claim is a convenience for the frontend only - every request is
    re-validated server-side against the live User.role in the database, so
    a stale or tampered claim can never grant access beyond what the DB
    currently allows.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["email"] = user.email
        return token
