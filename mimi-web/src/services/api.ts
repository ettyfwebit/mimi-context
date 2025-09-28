import axios, { AxiosResponse, AxiosError } from "axios";
import toast from "react-hot-toast";
import { config } from "@/utils/config";
import type {
  UploadResponse,
  RAGQueryResponse,
  RAGQueryRequest,
  AgentResponse,
  AgentRequest,
  AdminDocsResponse,
  AdminUpdatesResponse,
  HealthResponse,
} from "@/types/api";

// Create axios instance with base configuration
const api = axios.create({
  baseURL: config.apiBaseUrl,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add auth header if API key is provided
if (config.apiKey) {
  api.defaults.headers.common["Authorization"] = `Bearer ${config.apiKey}`;
}

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    const message = getErrorMessage(error);
    toast.error(message);

    // Log error details for debugging (no PII)
    console.error("API Error:", {
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      method: error.config?.method,
    });

    return Promise.reject(error);
  },
);

const getErrorMessage = (error: AxiosError): string => {
  if (error.code === "ECONNABORTED") {
    return "Request timeout. Please try again.";
  }

  if (!error.response) {
    return "Network error. Please check your connection.";
  }

  const status = error.response.status;
  const data = error.response.data as any;

  switch (status) {
    case 400:
      return data?.message || "Invalid request";
    case 401:
      return "Unauthorized. Please check your API key.";
    case 403:
      return "Access forbidden";
    case 404:
      return "Endpoint not found";
    case 429:
      return "Rate limit exceeded. Please try again later.";
    case 500:
      return "Server error. Please try again.";
    default:
      return data?.message || `Request failed (${status})`;
  }
};

// API methods
export const apiService = {
  // Upload file
  async uploadFile(file: File, path: string): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("path", path);

    const response = await api.post<UploadResponse>(
      "/ingest/upload",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      },
    );

    return response.data;
  },

  // RAG query
  async queryRAG(request: RAGQueryRequest): Promise<RAGQueryResponse> {
    const response = await api.post<RAGQueryResponse>("/rag/query", request);
    return response.data;
  },

  // Agent query (optional)
  async askAgent(request: AgentRequest): Promise<AgentResponse> {
    const response = await api.post<AgentResponse>("/agent/ask", request);
    return response.data;
  },

  // Check if agent endpoint is available
  async checkAgentAvailability(): Promise<boolean> {
    try {
      await api.options("/agent/ask");
      return true;
    } catch (error) {
      const axiosError = error as AxiosError;
      return axiosError.response?.status !== 404;
    }
  },

  // Admin - list documents
  async getDocuments(params?: {
    source?: string;
    limit?: number;
  }): Promise<AdminDocsResponse> {
    const response = await api.get<AdminDocsResponse>("/admin/docs", {
      params,
    });
    return response.data;
  },

  // Admin - list ingestion events
  async getUpdates(params?: { limit?: number }): Promise<AdminUpdatesResponse> {
    const response = await api.get<AdminUpdatesResponse>("/admin/updates", {
      params,
    });
    return response.data;
  },

  // Health check
  async getHealth(): Promise<HealthResponse> {
    const response = await api.get<HealthResponse>("/health");
    return response.data;
  },
};

export default apiService;
