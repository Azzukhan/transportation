import React, { createContext, useContext, useState, useCallback, useEffect } from "react";
import { configureAuthCallbacks } from "../api/apiClient";
import { loginUser, logoutUser, getUser } from "../api/authentication";
import type { AuthUser, LoginUserPayload } from "../types";

interface AuthContextType {
  isAuthenticated: boolean;
  user: AuthUser | null;
  accessToken: string | null;
  login: (payload: LoginUserPayload) => Promise<void>;
  logout: () => Promise<void>;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [accessToken, setAccessToken] = useState<string | null>(() =>
    localStorage.getItem("access_token")
  );
  const [refreshTokenVal, setRefreshTokenVal] = useState<string | null>(() =>
    localStorage.getItem("refresh_token")
  );
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = Boolean(accessToken);

  const handleLogout = useCallback(() => {
    setAccessToken(null);
    setRefreshTokenVal(null);
    setUser(null);
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  }, []);

  useEffect(() => {
    configureAuthCallbacks({
      getAccessToken: () => accessToken,
      getRefreshToken: () => refreshTokenVal,
      onTokenRefresh: (result) => {
        setAccessToken(result.accessToken);
        localStorage.setItem("access_token", result.accessToken);
        if (result.refreshToken) {
          setRefreshTokenVal(result.refreshToken);
          localStorage.setItem("refresh_token", result.refreshToken);
        }
      },
      onLogout: handleLogout,
    });
  }, [accessToken, refreshTokenVal, handleLogout]);

  useEffect(() => {
    const init = async () => {
      if (accessToken) {
        try {
          const userData = await getUser();
          setUser(userData);
        } catch {
          handleLogout();
        }
      }
      setIsLoading(false);
    };
    init();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const login = async (payload: LoginUserPayload) => {
    const result = await loginUser(payload);
    setAccessToken(result.accessToken);
    setUser(result.user);
    localStorage.setItem("access_token", result.accessToken);
    if (result.refreshToken) {
      setRefreshTokenVal(result.refreshToken);
      localStorage.setItem("refresh_token", result.refreshToken);
    }
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
    <AuthContext.Provider value={{ isAuthenticated, user, accessToken, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
};
