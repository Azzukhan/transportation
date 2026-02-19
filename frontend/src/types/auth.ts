export interface AuthUser {
  username: string;
  id?: number;
  email?: string;
}

export interface AuthState {
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
  user: AuthUser;
}

export interface TokenRefreshPayload {
  user: AuthUser | null;
}

export interface AuthTokenApiResponse {
  access_token?: string;
  refresh_token?: string;
  token_type: string;
  username?: string;
}

export interface RefreshTokenApiResponse {
  access_token?: string;
  refresh_token?: string;
  token_type?: string;
  username?: string;
}
