import axios, {
  AxiosHeaders,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from "axios";
import { config } from "../config";

type RetryableRequestConfig = InternalAxiosRequestConfig & { _retry?: boolean };
type QueueItem = { resolve: (token: string) => void; reject: (error: unknown) => void };
type RefreshResult = { accessToken: string; refreshToken: string | null };

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
let getAccessToken: () => string | null = () => null;
let getRefreshTokenValue: () => string | null = () => null;
let onTokenRefreshed: ((result: RefreshResult) => void) | null = null;
let onForceLogout: (() => void) | null = null;

export const configureAuthCallbacks = (callbacks: {
  getAccessToken: () => string | null;
  getRefreshToken: () => string | null;
  onTokenRefresh: (result: RefreshResult) => void;
  onLogout: () => void;
}) => {
  getAccessToken = callbacks.getAccessToken;
  getRefreshTokenValue = callbacks.getRefreshToken;
  onTokenRefreshed = callbacks.onTokenRefresh;
  onForceLogout = callbacks.onLogout;
};

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
  if (!url) return false;
  return url.includes("/auth/token") || url.includes("/auth/refresh") || url.includes("/auth/token/refresh");
};

const attachAccessToken = (request: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
  const token = getAccessToken();
  if (!token) return request;
  request.headers = request.headers ?? new AxiosHeaders();
  (request.headers as AxiosHeaders).set("Authorization", `Bearer ${token}`);
  return request;
};

export const performRefreshToken = async (refreshTokenVal: string): Promise<RefreshResult> => {
  const response = await baseClientV1.post<{ access_token: string; refresh_token?: string }>(
    "/auth/token/refresh",
    { refresh_token: refreshTokenVal },
  );
  return {
    accessToken: response.data.access_token,
    refreshToken: response.data.refresh_token ?? null,
  };
};

const setupInterceptors = (client: AxiosInstance): void => {
  client.interceptors.request.use(
    (req) => {
      if (isAuthRoute(req.url)) return req;
      return attachAccessToken(req);
    },
    (error) => Promise.reject(error),
  );

  client.interceptors.response.use(
    (res) => res,
    async (error) => {
      const originalRequest = error.config as RetryableRequestConfig | undefined;
      if (!originalRequest || error.response?.status !== 401 || originalRequest._retry || isAuthRoute(originalRequest.url)) {
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise<string>((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers = originalRequest.headers ?? new AxiosHeaders();
          (originalRequest.headers as AxiosHeaders).set("Authorization", `Bearer ${token}`);
          return client(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const storedRefresh = getRefreshTokenValue();
      if (!storedRefresh) {
        processQueue(error, null);
        isRefreshing = false;
        onForceLogout?.();
        return Promise.reject(error);
      }

      try {
        const refreshed = await performRefreshToken(storedRefresh);
        onTokenRefreshed?.(refreshed);
        processQueue(null, refreshed.accessToken);
        originalRequest.headers = originalRequest.headers ?? new AxiosHeaders();
        (originalRequest.headers as AxiosHeaders).set("Authorization", `Bearer ${refreshed.accessToken}`);
        return client(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        onForceLogout?.();
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    },
  );
};

setupInterceptors(baseClientV1);
setupInterceptors(baseClientV2);

export const apiClient = baseClientV1;
export const apiClientV2 = baseClientV2;
