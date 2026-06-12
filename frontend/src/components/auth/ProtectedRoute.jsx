import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { FullPageLoader } from "../shared/FullPageLoader";

export function ProtectedRoute({ children, roles }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) return <FullPageLoader />;
  if (!user) return <Navigate to="/login" replace state={{ from: location }} />;
  if (roles?.length && !roles.includes(user.role)) return <Navigate to="/dashboard" replace />;

  return children;
}

