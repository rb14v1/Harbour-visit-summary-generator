import { apiClient } from "./client";
import type { Paginated, Visit, VisitSummary } from "../types";

export interface VisitPayload {
  patient: number;
  visit_date: string;
  chief_complaint: string;
  clinical_notes: string;
  diagnosis: string;
  treatment_plan: string;
}

export function listVisits(params?: { patient?: number }) {
  return apiClient.get<Paginated<Visit>>("/visits/", { params });
}

export function getVisit(id: number) {
  return apiClient.get<Visit>(`/visits/${id}/`);
}

export function createVisit(payload: VisitPayload) {
  return apiClient.post<Visit>("/visits/", payload);
}

export function updateVisit(id: number, payload: Partial<VisitPayload>) {
  return apiClient.patch<Visit>(`/visits/${id}/`, payload);
}

export function deleteVisit(id: number) {
  return apiClient.delete(`/visits/${id}/`);
}

export function generateVisitSummary(id: number) {
  return apiClient.post<VisitSummary>(`/visits/${id}/generate-summary/`);
}

export function fetchVisitSummary(id: number) {
  return apiClient.get<VisitSummary>(`/visits/${id}/summary/`);
}
