export type Role = "clinician" | "patient";

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: Role;
  specialty: string | null;
  date_joined: string;
}

export interface Patient {
  id: number;
  full_name: string;
  date_of_birth: string;
  mrn: string;
  user: number | null;
  created_at: string;
  updated_at: string;
}

export interface Visit {
  id: number;
  patient: number;
  patient_name: string;
  patient_mrn: string;
  clinician: number;
  clinician_name: string;
  visit_date: string;
  chief_complaint: string;
  clinical_notes: string;
  diagnosis: string;
  treatment_plan: string;
  created_at: string;
  has_summary: boolean;
}

export interface VisitSummary {
  id: number;
  visit: number;
  patient_friendly_summary: string;
  generated_at: string;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
