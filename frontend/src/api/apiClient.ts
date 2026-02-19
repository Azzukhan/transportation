import axios, {
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from "axios";
import { config } from "../config";

type RetryableRequestConfig = InternalAxiosRequestConfig & { _retry?: boolean };
type QueueItem = { resolve: () => void; reject: (error: unknown) => void };

const REQUEST_TIMEOUT_MS = 15000;

const baseClientV1 = axios.create({
  baseURL: config.apiBaseUrl,
  timeout: REQUEST_TIMEOUT_MS,
  withCredentials: true,
});

const baseClientV2 = axios.create({
  baseURL: config.apiBaseUrlV2,
  timeout: REQUEST_TIMEOUT_MS,
  withCredentials: true,
});

let isRefreshing = false;
let failedQueue: QueueItem[] = [];
let onForceLogout: (() => void) | null = null;

export const configureAuthCallbacks = (callbacks: {
  onLogout: () => void;
}) => {
  onForceLogout = callbacks.onLogout;
};

const processQueue = (error: unknown): void => {
  failedQueue.forEach((queued) => {
    if (error) {
      queued.reject(error);
      return;
    }
    queued.resolve();
  });
  failedQueue = [];
};

const isAuthRoute = (url: string | undefined): boolean => {
  if (!url) return false;
  return url.includes("/auth/token") || url.includes("/auth/token/refresh");
};

const readCookie = (name: string): string | null => {
  if (typeof document === "undefined") return null;
  const item = document.cookie
    .split("; ")
    .find((entry) => entry.startsWith(`${name}=`));
  if (!item) return null;
  return decodeURIComponent(item.split("=", 2)[1] || "");
};

const attachCsrfHeader = (request: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
  const method = (request.method || "get").toUpperCase();
  if (!["POST", "PUT", "PATCH", "DELETE"].includes(method)) return request;
  const csrfToken = readCookie("csrf_token");
  if (!csrfToken) return request;
  request.headers = request.headers ?? {};
  request.headers["X-CSRF-Token"] = csrfToken;
  return request;
};

export const performRefreshToken = async (): Promise<void> => {
  await baseClientV1.post(
    "/auth/token/refresh",
    {},
    {
      headers: {
        "X-CSRF-Token": readCookie("csrf_token") || "",
      },
    },
  );
};

const setupInterceptors = (client: AxiosInstance): void => {
  client.interceptors.request.use(
    (req) => attachCsrfHeader(req),
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
        return new Promise<void>((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(() => {
          return client(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        await performRefreshToken();
        processQueue(null);
        return client(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError);
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
