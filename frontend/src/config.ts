const envOrDefault = (value: string | undefined, fallback: string): string => {
  return value || fallback;
};

export const config = {
  apiBaseUrl: envOrDefault(import.meta.env.VITE_API_BASE_URL, "http://localhost:8000/api/v1"),
  apiBaseUrlV2: envOrDefault(import.meta.env.VITE_API_BASE_URL_V2, "http://localhost:8000/api/v2"),
};

export type AppConfig = typeof config;
