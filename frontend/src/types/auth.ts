export interface AuthUser {
  username: string;
  id?: number;
  email?: string;
}

export interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: AuthUser | null;
  isAuthenticated: boolean;
}

export interface LoginUserPayload {
  username: string;
  password: string;
}

export interface SignupUserPayload {
  username: string;
  password: string;
  email?: string;
}

export interface LoginSuccessPayload {
  accessToken: string;
  refreshToken: string | null;
  user: AuthUser;
}

export interface TokenRefreshPayload {
  accessToken: string;
  refreshToken: string | null;
}

export interface AuthTokenApiResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
}

export interface RefreshTokenApiResponse {
  access_token: string;
  refresh_token?: string;
}
