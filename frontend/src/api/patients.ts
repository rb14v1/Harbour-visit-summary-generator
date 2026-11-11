import { apiClient } from "./client";
import type { Paginated, Patient } from "../types";

export interface PatientPayload {
  full_name: string;
  date_of_birth: string;
  mrn: string;
  user?: number | null;
}

export function listPatients() {
  return apiClient.get<Paginated<Patient>>("/patients/");
}

export function getPatient(id: number) {
  return apiClient.get<Patient>(`/patients/${id}/`);
}

export function createPatient(payload: PatientPayload) {
  return apiClient.post<Patient>("/patients/", payload);
}

export function updatePatient(id: number, payload: Partial<PatientPayload>) {
  return apiClient.patch<Patient>(`/patients/${id}/`, payload);
}

export function deletePatient(id: number) {
  return apiClient.delete(`/patients/${id}/`);
}
