"""
Dual-path AI layer: a real OpenAI chat-completion call when
`OPENAI_API_KEY` is set, otherwise a fully offline, deterministic stub. This
lets the entire visit-summary pipeline (migrations, seed data, the
generate-summary endpoint) be built, run, and tested with zero network
access and zero cost.

Unlike the sibling `ticket-triage` app, there is no embedding step and no
vector database here - plain Postgres only. This module has exactly one
entry point, `generate_visit_summary`, which turns a clinician's clinical
shorthand (chief complaint, clinical notes, diagnosis, treatment plan) into
a plain-language paragraph a patient can actually understand.

*** IMPORTANT ***: the stub path does NOT call any language model and does
NOT perform real jargon-to-plain-English translation - it deterministically
fills a fixed template with the actual diagnosis/treatment_plan/etc. text
supplied, so it reads as a reasonable patient summary even offline, and the
SAME input fields always produce the SAME stub output (this determinism is
relied on by tests and by the seed-data migration). Real plain-language
translation - actually rewriting clinical jargon into lay terms - requires
a real OPENAI_API_KEY so `generate_visit_summary` calls the real chat
completions API.
"""
from django.conf import settings

_SYSTEM_PROMPT = (
    "You are a clinical communication assistant. Translate a clinician's "
    "visit documentation into a short, warm, plain-language paragraph for "
    "the patient. Explain any medications, diagnoses, or instructions in "
    "everyday language a non-clinician can follow. Do not invent facts "
    "that are not supported by the provided fields. Write one paragraph, "
    "no headings or bullet points."
)


def is_stub_mode() -> bool:
    return not bool(settings.OPENAI_API_KEY)


def generate_visit_summary(
    chief_complaint: str,
    clinical_notes: str,
    diagnosis: str,
    treatment_plan: str,
) -> str:
    """Return a plain-language, patient-friendly summary paragraph for a
    visit, translating clinical jargon into something a patient can
    understand.

    Real path (OPENAI_API_KEY set): calls the OpenAI chat completions API
    with `settings.OPENAI_CHAT_MODEL`.
    Stub path (no key): deterministic templated paragraph built directly
    from the input fields - see module docstring.
    """
    if settings.OPENAI_API_KEY:
        from openai import OpenAI

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        user_content = (
            f"Chief complaint: {chief_complaint}\n"
            f"Clinical notes: {clinical_notes}\n"
            f"Diagnosis: {diagnosis}\n"
            f"Treatment plan: {treatment_plan}"
        )
        response = client.chat.completions.create(
            model=settings.OPENAI_CHAT_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )
        return response.choices[0].message.content

    return _stub_summary(chief_complaint, clinical_notes, diagnosis, treatment_plan)


def _stub_summary(chief_complaint: str, clinical_notes: str, diagnosis: str, treatment_plan: str) -> str:
    chief_complaint = (chief_complaint or "").strip()
    clinical_notes = (clinical_notes or "").strip()
    diagnosis = (diagnosis or "").strip()
    treatment_plan = (treatment_plan or "").strip()

    chief_part = (
        f"You came in because of {chief_complaint[0].lower() + chief_complaint[1:]}. "
        if chief_complaint else ""
    )
    diagnosis_part = (
        f"After your visit, your clinician's diagnosis was: {diagnosis}. "
        if diagnosis else "Your clinician did not record a specific diagnosis for this visit. "
    )
    plan_part = (
        f"Here is the plan going forward: {treatment_plan} "
        if treatment_plan else "No specific treatment plan was recorded for this visit. "
    )
    notes_part = (
        f"For your records, the clinician also noted: {clinical_notes} "
        if clinical_notes else ""
    )
    closing = (
        "If anything above is unclear, or you have questions about your "
        "diagnosis or how to follow the treatment plan, please contact "
        "your clinician's office before starting, stopping, or changing "
        "any medication."
    )

    return f"{chief_part}{diagnosis_part}{plan_part}{notes_part}{closing}"
