import { createContext, useContext, useEffect, useState } from "react";
import { authApi } from "../api/auth";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadProfile = async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      const { data } = await authApi.me();
      setUser(data);
    } catch {
      localStorage.removeItem("access_token");
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

  const login = async (payload) => {
    const { data } = await authApi.login(payload);
    localStorage.setItem("access_token", data.access_token);
    const profile = await authApi.me();
    setUser(profile.data);
    return profile.data;
  };

  const register = async (payload) => {
    await authApi.register(payload);
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } finally {
      localStorage.removeItem("access_token");
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, setUser, refreshProfile: loadProfile }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}

