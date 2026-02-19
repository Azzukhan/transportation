import { config } from "../config";

export const sensitiveExportStepUpHeaders = (): Record<string, string> => {
  const token = config.sensitiveExportStepUpToken.trim();
  if (!token) {
    return {};
  }
  return { "X-Step-Up-Token": token };
};
