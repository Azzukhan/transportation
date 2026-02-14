import type { PropsWithChildren } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { Spin } from "antd";

import { useAppSelector } from "../app/hooks";
import { selectIsAuthenticated } from "../features/auth/authSlice";
import { useInitializeAuth } from "../hooks";

type ProtectedRouteProps = PropsWithChildren & {
  redirectTo?: string;
};

export const ProtectedRoute = ({
  children,
  redirectTo = "/login",
}: ProtectedRouteProps) => {
  const location = useLocation();
  const isAuthenticated = useAppSelector(selectIsAuthenticated);
  const { isInitializingAuth } = useInitializeAuth();

  if (isInitializingAuth) {
    return <Spin size="large" style={{ margin: "80px auto", display: "block" }} />;
  }

  if (!isAuthenticated) {
    const redirect = encodeURIComponent(`${location.pathname}${location.search}`);
    return <Navigate to={`${redirectTo}?redirect=${redirect}`} replace />;
  }

  return <>{children}</>;
};
