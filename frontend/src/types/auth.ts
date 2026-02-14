export type AuthUser = {
  id?: string;
  username: string;
  email?: string;
};

export type LoginUserPayload = {
  username: string;
  password: string;
};

export type SignupUserPayload = {
  username: string;
  password: string;
  email?: string;
};

export type AuthTokenApiResponse = {
  access_token: string;
  token_type: string;
  refresh_token?: string;
};

export type RefreshTokenApiResponse = {
  access_token: string;
  refresh_token?: string;
  token_type?: string;
};

export type LoginSuccessPayload = {
  accessToken: string;
  refreshToken?: string | null;
  user?: AuthUser | null;
};

export type TokenRefreshPayload = {
  accessToken: string;
  refreshToken?: string | null;
};

export type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  user: AuthUser | null;
  isAuthenticated: boolean;
};
