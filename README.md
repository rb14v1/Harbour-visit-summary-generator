# Patient Visit Summary Generator

A clinician-facing app for recording patient visits and generating a
plain-language, patient-friendly summary of each visit with a single AI
call. Plain PostgreSQL only - no pgvector, no vector database of any kind.

Stack: React + Vite + TypeScript, Django REST Framework, PostgreSQL.

## The AI feature

`backend/apps/common/ai.py` exposes one function,
`generate_visit_summary(chief_complaint, clinical_notes, diagnosis,
treatment_plan)`, which translates a visit's clinical shorthand into a
plain-language paragraph a patient can understand.

- **Real path** (`OPENAI_API_KEY` set): calls the OpenAI chat completions
  API with `OPENAI_CHAT_MODEL` (default `gpt-5.6-sol`).
- **Stub path** (no key - the default for local dev/tests): a fully
  offline, deterministic template filled in from the visit's own fields.
  The same input always produces the same output, which the test suite
  and the seed-data migration both rely on.

Called synchronously from `VisitViewSet.generate_summary` (POST
`/api/visits/{id}/generate-summary/`) before responding - there's no
vector DB or other secondary store to desync here, so no
`transaction.on_commit` complexity is needed.

## Running with Docker (requires Docker)

```
cp .env.example .env
docker compose up --build
docker compose exec backend python manage.py createsuperuser
```

- Backend: http://localhost:8000/api/
- Frontend: http://localhost:5173/
- Admin: http://localhost:8000/admin/

## Running the backend without Docker

This machine has a native Postgres 18 instance running locally
(`visit_summary_generator` role/database already created), and
`backend/.env` is already configured to point at it with
`USE_SQLITE=False`.

```
cd backend
python -m venv venv
./venv/Scripts/activate        # or source venv/bin/activate on macOS/Linux
pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

### Dev-only SQLite override

For a machine with no local Postgres/Docker available, set `USE_SQLITE=True`
(default `True` at the `base.py` level, overridden to `False` in the real
`backend/.env`) so `manage.py check/makemigrations/test` can run with zero
external dependencies:

```
set USE_SQLITE=True            # PowerShell: $env:USE_SQLITE="True"
python manage.py test
```

**Never use this for a real deployment.**

## Demo login credentials

Seeded by the idempotent data migration `apps/visits/migrations/
0002_seed_demo_data.py` (get_or_create throughout, safe to re-run):

- Clinician: `clinician@example.com` / `demo12345`
- Patient (login only, no patient-facing API in this build): `patient@example.com` / `demo12345`

Seed data also includes 4 patients and 14 visits spanning a range of
conditions (sinusitis, migraine, hypertension, type 2 diabetes, ankle
sprain, UTI, allergic rhinitis, contact dermatitis, anxiety, bronchitis,
GERD, post-op follow-up), 12 of which already have a generated
patient-friendly summary.

## API surface

- `/api/auth/` - `register/`, `login/`, `refresh/`, `logout/` (JWT via
  djangorestframework-simplejwt; refresh tokens rotate and are blacklisted
  on rotation/logout)
- `/api/users/me/` - GET/PATCH the authenticated user's own profile
- `/api/patients/` - full CRUD, clinician-only
- `/api/visits/` - full CRUD; a clinician sees/edits only the visits they
  themselves recorded (queryset-scoped, so another clinician's visit 404s)
- `/api/visits/{id}/generate-summary/` - POST, creates/replaces the
  visit's `VisitSummary`
- `/api/visits/{id}/summary/` - GET, 404 until a summary has been
  generated

## Data model

- `apps.accounts.User` - custom user, email as `USERNAME_FIELD`, `role`
  (`clinician`/`patient`), `full_name`, nullable `specialty` (clinicians
  only).
- `apps.patients.Patient` - `full_name`, `date_of_birth`, unique `mrn`,
  and a nullable one-to-one `user` link so a patient can eventually log in
  and see their own data - deliberately left as a simple nullable link
  rather than a full patient-portal self-registration flow, which is out
  of scope for this build.
- `apps.visits.Visit` - `patient`, `clinician`, `visit_date`,
  `chief_complaint`, `clinical_notes`, `diagnosis`, `treatment_plan`.
- `apps.visits.VisitSummary` - one-to-one with `Visit`,
  `patient_friendly_summary`, `generated_at`. Regenerating replaces the
  existing row rather than creating a second one
  (`VisitSummary.objects.update_or_create`).

## Deviations from the original spec (and why)

- `/api/patients/` and `/api/visits/` are both clinician-only; there is no
  separate patient-facing API in this build. `Patient.user` exists so a
  patient-portal view could be added later without a schema change, but
  building that full self-service flow (registration linking, scoped
  visibility) was explicitly out of scope.
- Patient records are a shared clinic roster (any clinician can manage any
  patient), while `Visit` is scoped per-clinician - the spec only asked
  for ownership isolation on visits, not on the patient roster itself.
