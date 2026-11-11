import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { listVisits } from "../../api/visits";
import { extractErrorMessage } from "../../api/client";
import type { Visit } from "../../types";
import { VisitForm } from "./VisitForm";

export function VisitListPage() {
  const [searchParams] = useSearchParams();
  const patientFilter = searchParams.get("patient");
  const [visits, setVisits] = useState<Visit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);

  function load() {
    setLoading(true);
    listVisits(patientFilter ? { patient: Number(patientFilter) } : undefined)
      .then((res) => setVisits(res.data.results))
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setLoading(false));
  }

  useEffect(load, [patientFilter]);

  return (
    <div className="page">
      <div className="toolbar">
        <h1>Visits</h1>
        <button onClick={() => setShowForm((v) => !v)}>{showForm ? "Cancel" : "Record visit"}</button>
      </div>
      {error && <div className="form-error">{error}</div>}

      {showForm && (
        <VisitForm
          defaultPatientId={patientFilter ? Number(patientFilter) : undefined}
          onSaved={() => {
            setShowForm(false);
            load();
          }}
        />
      )}

      {loading ? (
        <p>Loading...</p>
      ) : (
        <ul className="entry-list">
          {visits.map((v) => (
            <li key={v.id} className="entry-card">
              <div className="entry-card-header">
                <strong>{v.patient_name}</strong>
                <span className="muted">MRN {v.patient_mrn}</span>
                <span className="muted">{v.visit_date}</span>
                {v.has_summary && <span className="visible-badge">Summary ready</span>}
              </div>
              <p className="entry-note">{v.chief_complaint}</p>
              <Link to={`/visits/${v.id}`}>View details</Link>
            </li>
          ))}
          {visits.length === 0 && <p className="muted">No visits recorded yet.</p>}
        </ul>
      )}
    </div>
  );
}
