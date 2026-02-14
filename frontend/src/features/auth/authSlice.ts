import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

import type {
  AuthState,
  AuthUser,
  LoginSuccessPayload,
  TokenRefreshPayload,
} from "../../types";
import type { RootState } from "../../app/store";

const initialState: AuthState = {
  accessToken: null,
  refreshToken: null,
  user: null,
  isAuthenticated: false,
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    onLoginSuccess: (state, action: PayloadAction<LoginSuccessPayload>) => {
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken ?? state.refreshToken;
      state.user = action.payload.user ?? state.user;
      state.isAuthenticated = true;
    },
    onTokenRefresh: (state, action: PayloadAction<TokenRefreshPayload>) => {
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken ?? state.refreshToken;
      state.isAuthenticated = Boolean(action.payload.accessToken);
    },
    onSetUser: (state, action: PayloadAction<AuthUser | null>) => {
      state.user = action.payload;
    },
    onLogout: (state) => {
      state.accessToken = null;
      state.refreshToken = null;
      state.user = null;
      state.isAuthenticated = false;
    },
  },
});

export const { onLoginSuccess, onTokenRefresh, onLogout, onSetUser } = authSlice.actions;

export const selectIsAuthenticated = (state: RootState): boolean => state.auth.isAuthenticated;
export const selectAccessToken = (state: RootState): string | null => state.auth.accessToken;
export const selectRefreshToken = (state: RootState): string | null => state.auth.refreshToken;
export const selectUser = (state: RootState): AuthUser | null => state.auth.user;

export const authReducer = authSlice.reducer;
