from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.ai import generate_visit_summary
from apps.common.permissions import IsClinician
from apps.visits.models import Visit, VisitSummary
from apps.visits.serializers import VisitSerializer, VisitSummarySerializer


class VisitViewSet(viewsets.ModelViewSet):
    """
    A clinician sees/edits only the visits they themselves recorded - the
    queryset is hard-scoped to `clinician=request.user`, so requesting
    another clinician's visit (by id) 404s rather than 403s, the same way
    the sibling `ticket-triage` app scopes Ticket to `user=request.user`.
    """

    serializer_class = VisitSerializer
    permission_classes = [permissions.IsAuthenticated, IsClinician]
    filterset_fields = ["patient"]

    def get_queryset(self):
        return (
            Visit.objects.filter(clinician=self.request.user)
            .select_related("patient", "clinician")
            .prefetch_related("summary")
        )

    def perform_create(self, serializer):
        serializer.save(clinician=self.request.user)

    @action(detail=True, methods=["post"], url_path="generate-summary")
    def generate_summary(self, request, pk=None):
        """Call the AI layer and create/replace this visit's VisitSummary.
        Synchronous: there is no vector DB or other secondary store to
        desync here, so a plain function call before responding is
        sufficient (no transaction.on_commit needed)."""
        visit = self.get_object()

        summary_text = generate_visit_summary(
            chief_complaint=visit.chief_complaint,
            clinical_notes=visit.clinical_notes,
            diagnosis=visit.diagnosis,
            treatment_plan=visit.treatment_plan,
        )

        summary, created = VisitSummary.objects.update_or_create(
            visit=visit,
            defaults={"patient_friendly_summary": summary_text},
        )

        response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(VisitSummarySerializer(summary).data, status=response_status)

    @action(detail=True, methods=["get"], url_path="summary")
    def summary(self, request, pk=None):
        visit = self.get_object()
        summary = getattr(visit, "summary", None)
        if summary is None:
            return Response(
                {"detail": "No summary has been generated for this visit yet."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(VisitSummarySerializer(summary).data)
