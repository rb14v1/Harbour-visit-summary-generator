import { createBrowserRouter, Navigate } from "react-router-dom";

import { ProtectedRoute } from "../auth/ProtectedRoute";
import { LoginPage } from "../features/onboarding/LoginPage";
import { PatientListPage } from "../features/patients/PatientListPage";
import { VisitDetailPage } from "../features/visits/VisitDetailPage";
import { VisitListPage } from "../features/visits/VisitListPage";
import { ClinicianLayout } from "../layouts/ClinicianLayout";
import { RoleHome } from "./RoleHome";

export const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  { path: "/", element: <RoleHome /> },

  {
    element: <ProtectedRoute allowedRoles={["clinician"]} />,
    children: [
      {
        element: <ClinicianLayout />,
        children: [
          { path: "/patients", element: <PatientListPage /> },
          { path: "/visits", element: <VisitListPage /> },
          { path: "/visits/:visitId", element: <VisitDetailPage /> },
        ],
      },
    ],
  },

  { path: "*", element: <Navigate to="/" replace /> },
]);
