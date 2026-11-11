import { useEffect, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";

import { createPatient, listPatients } from "../../api/patients";
import { extractErrorMessage } from "../../api/client";
import type { Patient } from "../../types";

export function PatientListPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [fullName, setFullName] = useState("");
  const [dob, setDob] = useState("");
  const [mrn, setMrn] = useState("");

  function load() {
    setLoading(true);
    listPatients()
      .then((res) => setPatients(res.data.results))
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await createPatient({ full_name: fullName, date_of_birth: dob, mrn });
      setFullName("");
      setDob("");
      setMrn("");
      setShowForm(false);
      load();
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  }

  return (
    <div className="page">
      <div className="toolbar">
        <h1>Patients</h1>
        <button onClick={() => setShowForm((v) => !v)}>{showForm ? "Cancel" : "Add patient"}</button>
      </div>
      {error && <div className="form-error">{error}</div>}

      {showForm && (
        <form className="card" onSubmit={handleCreate}>
          <div className="inline-fields">
            <label>
              Full name
              <input value={fullName} onChange={(e) => setFullName(e.target.value)} required />
            </label>
            <label>
              Date of birth
              <input type="date" value={dob} onChange={(e) => setDob(e.target.value)} required />
            </label>
            <label>
              MRN
              <input value={mrn} onChange={(e) => setMrn(e.target.value)} required />
            </label>
          </div>
          <button type="submit">Save patient</button>
        </form>
      )}

      {loading ? (
        <p>Loading...</p>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>MRN</th>
              <th>Date of birth</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {patients.map((p) => (
              <tr key={p.id}>
                <td>{p.full_name}</td>
                <td>{p.mrn}</td>
                <td>{p.date_of_birth}</td>
                <td>
                  <Link to={`/visits?patient=${p.id}`}>View visits</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
