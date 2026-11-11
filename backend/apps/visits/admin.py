from django.contrib import admin

from apps.visits.models import Visit, VisitSummary


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ["id", "patient", "clinician", "visit_date", "created_at"]
    list_filter = ["visit_date"]
    search_fields = ["patient__full_name", "patient__mrn", "chief_complaint", "diagnosis"]


@admin.register(VisitSummary)
class VisitSummaryAdmin(admin.ModelAdmin):
    list_display = ["id", "visit", "generated_at"]
