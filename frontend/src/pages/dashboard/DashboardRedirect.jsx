import { Navigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export function DashboardRedirect() {
  const { user } = useAuth();
  if (user?.role === "Doctor") return <Navigate to="/dashboard/doctor" replace />;
  if (user?.role === "Patient") return <Navigate to="/dashboard/patient" replace />;
  return <Navigate to="/dashboard/admin" replace />;
}

