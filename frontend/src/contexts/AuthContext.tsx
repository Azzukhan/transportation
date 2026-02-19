import React, { createContext, useContext, useState, useCallback, useEffect } from "react";
import { configureAuthCallbacks } from "../api/apiClient";
import { loginUser, logoutUser, getUser } from "../api/authentication";
import type { AuthUser, LoginUserPayload } from "../types";

interface AuthContextType {
  isAuthenticated: boolean;
  user: AuthUser | null;
  login: (payload: LoginUserPayload) => Promise<void>;
  logout: () => Promise<void>;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = Boolean(user);

  const handleLogout = useCallback(() => {
    setUser(null);
  }, []);

  useEffect(() => {
    configureAuthCallbacks({
      onLogout: handleLogout,
    });
  }, [handleLogout]);

  useEffect(() => {
    const init = async () => {
      try {
        const userData = await getUser();
        setUser(userData);
      } catch {
        handleLogout();
      }
      setIsLoading(false);
    };
    init();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const login = async (payload: LoginUserPayload) => {
    const result = await loginUser(payload);
    setUser(result.user);
  };

  const logout = async () => {
    try {
      await logoutUser();
    } catch {
      // ignore
    }
    handleLogout();
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
};
