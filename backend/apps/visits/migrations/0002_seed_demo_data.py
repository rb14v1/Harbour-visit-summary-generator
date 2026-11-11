"""
Idempotent demo/seed data (get_or_create throughout, safe to run on every
`manage.py migrate`): one demo clinician, one demo patient-role login, a
handful of Patient records, and a spread of realistic Visit rows - most
with a generated VisitSummary, a couple left pending to demonstrate the
"not yet generated" state.

Summaries are produced by calling the REAL `generate_visit_summary()`
function (apps/common/ai.py). At migrate time OPENAI_API_KEY is unset, so
this resolves to the deterministic offline stub - meaning anyone running a
fresh `manage.py migrate` (with no API key configured) gets byte-identical
seed summaries to what shipped here.
"""
from datetime import date

from django.contrib.auth.hashers import make_password
from django.db import migrations

# Historical models (via apps.get_model) do NOT carry AbstractBaseUser's
# methods (set_password/check_password) - only fields + Meta survive into
# migration state. Hash the demo password directly with make_password and
# write it straight to the `password` field instead.
_DEMO_PASSWORD_HASH = make_password("demo12345")


def seed_demo_data(apps, schema_editor):
    from apps.common.ai import generate_visit_summary

    User = apps.get_model("accounts", "User")
    Patient = apps.get_model("patients", "Patient")
    Visit = apps.get_model("visits", "Visit")
    VisitSummary = apps.get_model("visits", "VisitSummary")

    clinician, _created = User.objects.get_or_create(
        email="clinician@example.com",
        defaults={
            "full_name": "Dr. Dana Price",
            "role": "clinician",
            "specialty": "general_medicine",
            "is_active": True,
            "password": _DEMO_PASSWORD_HASH,
        },
    )

    patient_login, _created = User.objects.get_or_create(
        email="patient@example.com",
        defaults={
            "full_name": "Maria Gonzalez",
            "role": "patient",
            "is_active": True,
            "password": _DEMO_PASSWORD_HASH,
        },
    )

    patients_data = [
        dict(full_name="Maria Gonzalez", date_of_birth=date(1985, 4, 12), mrn="DEMO-0001", user=patient_login),
        dict(full_name="James Carter", date_of_birth=date(1972, 11, 3), mrn="DEMO-0002"),
        dict(full_name="Linda Chen", date_of_birth=date(1990, 7, 22), mrn="DEMO-0003"),
        dict(full_name="Robert Okafor", date_of_birth=date(1960, 1, 30), mrn="DEMO-0004"),
    ]

    patients = {}
    for data in patients_data:
        mrn = data.pop("mrn")
        patient, _ = Patient.objects.get_or_create(mrn=mrn, defaults=data)
        patients[mrn] = patient

    visits_data = [
        dict(
            mrn="DEMO-0001", visit_date=date(2026, 1, 8),
            chief_complaint="Productive cough and facial pressure for 6 days.",
            clinical_notes="Afebrile. Maxillary sinus tenderness bilaterally. Purulent nasal discharge. Sx >7 days without improvement.",
            diagnosis="Acute bacterial sinusitis.",
            treatment_plan="Amoxicillin 500mg TID x7d. Saline nasal irrigation. Return if symptoms worsen or persist beyond 10 days.",
            generate=True,
        ),
        dict(
            mrn="DEMO-0001", visit_date=date(2026, 2, 2),
            chief_complaint="Follow-up for sinusitis, feeling much better.",
            clinical_notes="Symptoms resolved. Lungs clear. No sinus tenderness.",
            diagnosis="Resolved acute bacterial sinusitis.",
            treatment_plan="No further antibiotics needed. Routine follow-up in 1 year.",
            generate=True,
        ),
        dict(
            mrn="DEMO-0001", visit_date=date(2026, 3, 20),
            chief_complaint="Recurring throbbing headaches, worse with light.",
            clinical_notes="Unilateral throbbing HA, photophobia and nausea, 4-6 hrs duration, 2x/month. Normal neuro exam.",
            diagnosis="Migraine without aura.",
            treatment_plan="Sumatriptan 50mg at onset of attack, max 2 doses/24h. Keep a headache diary. Avoid known triggers.",
            generate=True,
        ),
        dict(
            mrn="DEMO-0002", visit_date=date(2026, 1, 14),
            chief_complaint="Routine blood pressure check.",
            clinical_notes="BP 148/94 seated, repeat 146/92. No chest pain, no SOB. Weight stable.",
            diagnosis="Hypertension, stage 1, uncontrolled.",
            treatment_plan="Start lisinopril 10mg once daily. Low-sodium diet, home BP monitoring. Recheck in 4 weeks.",
            generate=True,
        ),
        dict(
            mrn="DEMO-0002", visit_date=date(2026, 2, 18),
            chief_complaint="Follow-up blood pressure check.",
            clinical_notes="BP 132/84 on lisinopril, well tolerated, no side effects reported.",
            diagnosis="Hypertension, stage 1, improved control.",
            treatment_plan="Continue lisinopril 10mg daily. Continue home monitoring. Recheck in 3 months.",
            generate=True,
        ),
        dict(
            mrn="DEMO-0002", visit_date=date(2026, 4, 2),
            chief_complaint="Increased thirst, frequent urination, fatigue.",
            clinical_notes="Random glucose 212 mg/dL. A1c 7.8%. BMI 31. Family history of type 2 diabetes.",
            diagnosis="Type 2 diabetes mellitus, newly diagnosed.",
            treatment_plan="Start metformin 500mg BID with meals. Dietician referral. Recheck A1c in 3 months.",
            generate=True,
        ),
        dict(
            mrn="DEMO-0002", visit_date=date(2026, 5, 29),
            chief_complaint="Ankle pain after missing a step yesterday.",
            clinical_notes="Swelling and tenderness over lateral malleolus. Able to bear weight. Negative Ottawa ankle rules for fracture.",
            diagnosis="Grade 1 lateral ankle sprain.",
            treatment_plan="RICE protocol (rest, ice, compression, elevation). OTC ibuprofen as needed. Ankle brace for 2 weeks.",
            generate=True,
        ),
        dict(
            mrn="DEMO-0003", visit_date=date(2026, 1, 25),
            chief_complaint="Burning with urination and urinary urgency for 2 days.",
            clinical_notes="Urinalysis positive for leukocyte esterase and nitrites. No fever, no flank pain.",
            diagnosis="Uncomplicated urinary tract infection.",
            treatment_plan="Nitrofurantoin 100mg BID x5 days. Increase fluid intake. Return if fever or back pain develops.",
            generate=True,
        ),
        dict(
            mrn="DEMO-0003", visit_date=date(2026, 3, 6),
            chief_complaint="Sneezing, itchy watery eyes, nasal congestion each spring.",
            clinical_notes="Clear rhinorrhea, boggy nasal turbinates, no fever. Pattern consistent with seasonal allergies.",
            diagnosis="Seasonal allergic rhinitis.",
            treatment_plan="Daily non-drowsy antihistamine (cetirizine 10mg). Intranasal corticosteroid spray during peak season.",
            generate=True,
        ),
        dict(
            mrn="DEMO-0003", visit_date=date(2026, 4, 17),
            chief_complaint="Itchy, red rash on both forearms for a week.",
            clinical_notes="Erythematous, scaly patches on volar forearms, mild excoriation. No new soaps or detergents identified yet.",
            diagnosis="Contact dermatitis.",
            treatment_plan="Topical hydrocortisone 1% BID x7d. Avoid suspected irritants. Follow up if not improved in 2 weeks.",
            generate=True,
        ),
        dict(
            mrn="DEMO-0003", visit_date=date(2026, 6, 9),
            chief_complaint="Feeling anxious and overwhelmed most days for the past month.",
            clinical_notes="Reports racing thoughts, trouble sleeping, difficulty concentrating at work. No safety concerns. PHQ-9/GAD-7 administered.",
            diagnosis="Generalized anxiety disorder.",
            treatment_plan="Referral to counseling for CBT. Sleep hygiene education. Follow up in 4 weeks to reassess and discuss medication options.",
            generate=False,
        ),
        dict(
            mrn="DEMO-0004", visit_date=date(2026, 2, 11),
            chief_complaint="Persistent cough with chest tightness for 10 days, started after a cold.",
            clinical_notes="Scattered wheezes bilaterally, no fever, O2 sat 97% on room air. No prior history of asthma.",
            diagnosis="Acute bronchitis.",
            treatment_plan="Albuterol inhaler as needed for wheeze/cough. Increase fluids and rest. Return if fever or worsening shortness of breath.",
            generate=True,
        ),
        dict(
            mrn="DEMO-0004", visit_date=date(2026, 3, 30),
            chief_complaint="Burning chest discomfort after meals and when lying down.",
            clinical_notes="Postprandial retrosternal burning, worse supine, relieved partially by antacids. No alarm features.",
            diagnosis="Gastroesophageal reflux disease (GERD).",
            treatment_plan="Omeprazole 20mg once daily before breakfast. Avoid late meals, caffeine, and alcohol. Elevate head of bed.",
            generate=True,
        ),
        dict(
            mrn="DEMO-0004", visit_date=date(2026, 6, 15),
            chief_complaint="Two-week post-op check after knee arthroscopy.",
            clinical_notes="Incisions healing well, no signs of infection. Mild residual swelling. Range of motion improving with physical therapy.",
            diagnosis="Routine post-operative recovery, knee arthroscopy.",
            treatment_plan="Continue physical therapy 2x/week. Gradually increase weight-bearing activity as tolerated. Follow up in 1 month.",
            generate=False,
        ),
    ]

    for data in visits_data:
        mrn = data.pop("mrn")
        should_generate = data.pop("generate")
        patient = patients[mrn]
        visit, _ = Visit.objects.get_or_create(
            patient=patient,
            visit_date=data["visit_date"],
            chief_complaint=data["chief_complaint"],
            defaults={
                "clinician": clinician,
                "clinical_notes": data["clinical_notes"],
                "diagnosis": data["diagnosis"],
                "treatment_plan": data["treatment_plan"],
            },
        )

        if should_generate and not VisitSummary.objects.filter(visit=visit).exists():
            summary_text = generate_visit_summary(
                chief_complaint=visit.chief_complaint,
                clinical_notes=visit.clinical_notes,
                diagnosis=visit.diagnosis,
                treatment_plan=visit.treatment_plan,
            )
            VisitSummary.objects.get_or_create(
                visit=visit, defaults={"patient_friendly_summary": summary_text}
            )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("visits", "0001_initial"),
        ("patients", "0001_initial"),
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_demo_data, noop_reverse),
    ]
