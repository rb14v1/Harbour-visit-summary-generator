import { apiClient } from "./client";
import type { Role, User } from "../types";

export interface RegisterPayload {
  email: string;
  password: string;
  full_name?: string;
  role: Role;
  specialty?: string;
}

export function register(payload: RegisterPayload) {
  return apiClient.post<User>("/auth/register/", payload);
}

export function login(email: string, password: string) {
  return apiClient.post<{ access: string; refresh: string }>("/auth/login/", { email, password });
}

export function logout(refresh: string) {
  return apiClient.post("/auth/logout/", { refresh });
}

export function fetchMe() {
  return apiClient.get<User>("/users/me/");
}

export function updateMe(data: Partial<Pick<User, "full_name" | "specialty">>) {
  return apiClient.patch<User>("/users/me/", data);
}
