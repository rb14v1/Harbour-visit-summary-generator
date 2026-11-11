import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { extractErrorMessage } from "../../api/client";
import { fetchVisitSummary, generateVisitSummary, getVisit } from "../../api/visits";
import type { Visit, VisitSummary } from "../../types";

export function VisitDetailPage() {
  const { visitId } = useParams();
  const id = Number(visitId);
  const [visit, setVisit] = useState<Visit | null>(null);
  const [summary, setSummary] = useState<VisitSummary | null>(null);
  const [error, setError] = useState("");
  const [generating, setGenerating] = useState(false);

  function loadSummary() {
    fetchVisitSummary(id)
      .then((res) => setSummary(res.data))
      .catch(() => setSummary(null));
  }

  useEffect(() => {
    getVisit(id)
      .then((res) => setVisit(res.data))
      .catch((err) => setError(extractErrorMessage(err)));
    loadSummary();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  async function handleGenerate() {
    setError("");
    setGenerating(true);
    try {
      const res = await generateVisitSummary(id);
      setSummary(res.data);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setGenerating(false);
    }
  }

  if (error) return <div className="form-error">{error}</div>;
  if (!visit) return <p>Loading...</p>;

  return (
    <div className="page">
      <h1>
        {visit.patient_name} <span className="muted">MRN {visit.patient_mrn}</span>
      </h1>
      <p className="subtitle">{visit.visit_date}</p>

      <div className="card">
        <h3>Chief complaint</h3>
        <p>{visit.chief_complaint}</p>
        <h3>Clinical notes</h3>
        <p>{visit.clinical_notes}</p>
        <h3>Diagnosis</h3>
        <p>{visit.diagnosis}</p>
        <h3>Treatment plan</h3>
        <p>{visit.treatment_plan}</p>
      </div>

      <div className="card">
        <div className="toolbar">
          <h3>Patient-friendly summary</h3>
          <button onClick={handleGenerate} disabled={generating}>
            {generating ? "Generating..." : summary ? "Regenerate" : "Generate summary"}
          </button>
        </div>
        {summary ? (
          <>
            <p className="entry-note">{summary.patient_friendly_summary}</p>
            <p className="muted">Generated {new Date(summary.generated_at).toLocaleString()}</p>
          </>
        ) : (
          <p className="muted">No summary generated yet.</p>
        )}
      </div>
    </div>
  );
}
