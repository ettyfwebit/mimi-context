import type { AppConfig } from "@/types/api";

export const getConfig = (): AppConfig => {
  const apiBaseUrl =
    import.meta.env.VITE_MIMI_API_BASE || "http://localhost:8080";
  const apiKey = import.meta.env.VITE_MIMI_API_KEY;
  const defaultTopK = parseInt(
    import.meta.env.VITE_MIMI_DEFAULT_TOP_K || "5",
    10,
  );
  const defaultModel = import.meta.env.VITE_MIMI_DEFAULT_MODEL;
  const confidenceThreshold = parseFloat(
    import.meta.env.VITE_MIMI_CONFIDENCE_THRESHOLD || "0.30",
  );

  return {
    apiBaseUrl,
    apiKey,
    defaultTopK,
    defaultModel,
    confidenceThreshold,
  };
};

export const config = getConfig();
