const requiredEnv = (value: string | undefined, key: string): string => {
  if (!value) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
  return value;
};

export const config = {
  apiBaseUrl: requiredEnv(import.meta.env.VITE_API_BASE_URL, "VITE_API_BASE_URL"),
  apiBaseUrlV2: requiredEnv(
    import.meta.env.VITE_API_BASE_URL_V2,
    "VITE_API_BASE_URL_V2",
  ),
};

export type AppConfig = typeof config;
