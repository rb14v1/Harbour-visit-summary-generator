import { useEffect, useState, type FormEvent } from "react";

import { extractErrorMessage } from "../../api/client";
import { listPatients } from "../../api/patients";
import { createVisit } from "../../api/visits";
import type { Patient } from "../../types";

export function VisitForm({ defaultPatientId, onSaved }: { defaultPatientId?: number; onSaved: () => void }) {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [patientId, setPatientId] = useState<number | "">(defaultPatientId ?? "");
  const [visitDate, setVisitDate] = useState("");
  const [chiefComplaint, setChiefComplaint] = useState("");
  const [clinicalNotes, setClinicalNotes] = useState("");
  const [diagnosis, setDiagnosis] = useState("");
  const [treatmentPlan, setTreatmentPlan] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    listPatients().then((res) => setPatients(res.data.results));
  }, []);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!patientId) {
      setError("Select a patient.");
      return;
    }
    setError("");
    setSubmitting(true);
    try {
      await createVisit({
        patient: patientId,
        visit_date: visitDate,
        chief_complaint: chiefComplaint,
        clinical_notes: clinicalNotes,
        diagnosis,
        treatment_plan: treatmentPlan,
      });
      onSaved();
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      {error && <div className="form-error">{error}</div>}
      <label>
        Patient
        <select value={patientId} onChange={(e) => setPatientId(Number(e.target.value))} required>
          <option value="">Select a patient...</option>
          {patients.map((p) => (
            <option key={p.id} value={p.id}>
              {p.full_name} (MRN {p.mrn})
            </option>
          ))}
        </select>
      </label>
      <label>
        Visit date
        <input type="date" value={visitDate} onChange={(e) => setVisitDate(e.target.value)} required />
      </label>
      <label>
        Chief complaint
        <textarea value={chiefComplaint} onChange={(e) => setChiefComplaint(e.target.value)} required />
      </label>
      <label>
        Clinical notes
        <textarea value={clinicalNotes} onChange={(e) => setClinicalNotes(e.target.value)} required />
      </label>
      <label>
        Diagnosis
        <textarea value={diagnosis} onChange={(e) => setDiagnosis(e.target.value)} required />
      </label>
      <label>
        Treatment plan
        <textarea value={treatmentPlan} onChange={(e) => setTreatmentPlan(e.target.value)} required />
      </label>
      <button type="submit" disabled={submitting}>
        {submitting ? "Saving..." : "Save visit"}
      </button>
    </form>
  );
}
