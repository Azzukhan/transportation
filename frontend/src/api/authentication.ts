import axios from "axios";
import { apiClient, performRefreshToken } from "./apiClient";
import type {
  AuthTokenApiResponse,
  AuthUser,
  LoginSuccessPayload,
  LoginUserPayload,
  SignupUserPayload,
  TokenRefreshPayload,
} from "../types";

const isNotFound = (error: unknown): boolean =>
  axios.isAxiosError(error) && error.response?.status === 404;

export const loginUser = async (payload: LoginUserPayload): Promise<LoginSuccessPayload> => {
  const response = await apiClient.post<AuthTokenApiResponse>("/auth/token", payload);
  const userName = response.data.username ?? payload.username;
  return {
    user: { username: userName },
  };
};

export const signupUser = async (payload: SignupUserPayload): Promise<void> => {
  try {
    await apiClient.post("/auth/signup", payload);
  } catch (error) {
    if (isNotFound(error)) throw new Error("Signup endpoint is not available.");
    throw error;
  }
};

export const refreshToken = async (refreshTokenValue: string): Promise<TokenRefreshPayload> => {
  void refreshTokenValue;
  await performRefreshToken();
  const user = await getUser();
  return { user };
};

export const logoutUser = async (): Promise<void> => {
  try {
    await apiClient.post("/auth/logout");
  } catch (error) {
    if (!isNotFound(error)) throw error;
  }
};

export const getUser = async (): Promise<AuthUser | null> => {
  try {
    const response = await apiClient.get<AuthUser>("/auth/me");
    return response.data;
  } catch (error) {
    if (isNotFound(error)) return null;
    if (axios.isAxiosError(error) && error.response?.status === 401) return null;
    throw error;
  }
};
