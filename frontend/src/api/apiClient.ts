import axios, {
  AxiosHeaders,
  AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from "axios";

import { config } from "../config";
import { store } from "../app/store";
import { onLogout, onTokenRefresh } from "../features/auth/authSlice";
import type { RefreshTokenApiResponse } from "../types";

type RetryableRequestConfig = InternalAxiosRequestConfig & {
  _retry?: boolean;
};

type QueueItem = {
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
};

type RefreshResult = {
  accessToken: string;
  refreshToken: string | null;
};

const REQUEST_TIMEOUT_MS = 15000;

const baseClientV1 = axios.create({
  baseURL: config.apiBaseUrl,
  timeout: REQUEST_TIMEOUT_MS,
});

const baseClientV2 = axios.create({
  baseURL: config.apiBaseUrlV2,
  timeout: REQUEST_TIMEOUT_MS,
});

let isRefreshing = false;
let failedQueue: QueueItem[] = [];

const processQueue = (error: unknown, token: string | null): void => {
  failedQueue.forEach((queued) => {
    if (error || !token) {
      queued.reject(error);
      return;
    }
    queued.resolve(token);
  });
  failedQueue = [];
};

const isAuthRoute = (url: string | undefined): boolean => {
  if (!url) {
    return false;
  }
  return (
    url.includes("/auth/token") ||
    url.includes("/auth/refresh") ||
    url.includes("/auth/token/refresh")
  );
};

const attachAccessToken = (request: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
  const token = store.getState().auth.accessToken;
  if (!token) {
    return request;
  }

  request.headers = request.headers ?? new AxiosHeaders();
  request.headers.set("Authorization", `Bearer ${token}`);
  return request;
};

const tryRefreshEndpoint = async (
  client: AxiosInstance,
  endpoint: string,
  refreshToken: string,
): Promise<RefreshTokenApiResponse> => {
  const firstAttempt = await client.post<RefreshTokenApiResponse>(endpoint, {
    refresh_token: refreshToken,
  });

  if (firstAttempt.data.access_token) {
    return firstAttempt.data;
  }

  const secondAttempt = await client.post<RefreshTokenApiResponse>(endpoint, {
    refreshToken,
  });
  return secondAttempt.data;
};

export const performRefreshToken = async (refreshToken: string): Promise<RefreshResult> => {
  const refreshClient = axios.create({
    baseURL: config.apiBaseUrl,
    timeout: REQUEST_TIMEOUT_MS,
  });

  const endpoints = ["/auth/refresh", "/auth/token/refresh"];
  let lastError: unknown = null;

  for (const endpoint of endpoints) {
    try {
      const result = await tryRefreshEndpoint(refreshClient, endpoint, refreshToken);
      return {
        accessToken: result.access_token,
        refreshToken: result.refresh_token ?? refreshToken,
      };
    } catch (error) {
      lastError = error;
    }
  }

  throw lastError ?? new Error("Token refresh failed.");
};

const attachInterceptors = (client: AxiosInstance): AxiosInstance => {
  client.interceptors.request.use(attachAccessToken);

  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError): Promise<unknown> => {
      const originalRequest = error.config as RetryableRequestConfig | undefined;
      const statusCode = error.response?.status;

      if (!originalRequest || statusCode !== 401 || originalRequest._retry || isAuthRoute(originalRequest.url)) {
        return Promise.reject(error);
      }

      originalRequest._retry = true;

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({
            resolve: (token) => {
              originalRequest.headers = originalRequest.headers ?? new AxiosHeaders();
              originalRequest.headers.set("Authorization", `Bearer ${token}`);
              resolve(client(originalRequest));
            },
            reject,
          });
        });
      }

      isRefreshing = true;

      try {
        const refreshToken = store.getState().auth.refreshToken;
        if (!refreshToken) {
          throw new Error("Missing refresh token.");
        }

        const refreshed = await performRefreshToken(refreshToken);
        store.dispatch(
          onTokenRefresh({
            accessToken: refreshed.accessToken,
            refreshToken: refreshed.refreshToken,
          }),
        );

        processQueue(null, refreshed.accessToken);

        originalRequest.headers = originalRequest.headers ?? new AxiosHeaders();
        originalRequest.headers.set("Authorization", `Bearer ${refreshed.accessToken}`);
        return client(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        store.dispatch(onLogout());
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    },
  );

  return client;
};

export const apiClient = attachInterceptors(baseClientV1);
export const apiClientV2 = attachInterceptors(baseClientV2);
