import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";

export function ClinicianLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <header className="app-header">
        <span className="brand">Patient Visit Summary Generator</span>
        <nav className="main-nav">
          <NavLink to="/patients" className={({ isActive }) => (isActive ? "active" : "")}>
            Patients
          </NavLink>
          <NavLink to="/visits" className={({ isActive }) => (isActive ? "active" : "")}>
            Visits
          </NavLink>
        </nav>
        <div className="header-right">
          <span className="user-chip">{user?.full_name || user?.email}</span>
          <button className="btn-secondary" onClick={logout}>
            Log out
          </button>
        </div>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
