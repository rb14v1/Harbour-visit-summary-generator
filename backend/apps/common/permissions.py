from rest_framework.permissions import BasePermission


class IsClinician(BasePermission):
    """Grants access only to authenticated users with role='clinician'.
    Used to gate the patients and visits endpoints, which are
    clinician-only in this app (patients do not get a self-service API -
    see README)."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_clinician", False)
        )
