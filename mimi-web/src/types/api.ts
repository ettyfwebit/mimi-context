// API Response Types
export interface UploadResponse {
  ok: boolean;
  doc_id: string;
  chunks: number;
}

export interface Chunk {
  chunk_id: string;
  doc_id: string;
  source: string;
  path: string;
  score: number;
  snippet: string;
  full_text?: string;
  section_title?: string;
  char_start?: number;
  char_end?: number;
}

export interface RAGQueryResponse {
  chunks: Chunk[];
}

export interface Citation {
  doc_id: string;
  path: string;
}

export interface AgentResponse {
  answer: string;
  citations: Citation[];
  raw_chunks: Chunk[];
}

export interface Document {
  doc_id: string;
  source: string;
  path: string;
  updated_at: string;
  lang?: string;
  hash?: string;
}

export interface AdminDocsResponse {
  documents: Document[];
}

export interface IngestionEvent {
  id: string;
  time: string;
  type: string;
  ref: string;
  status: "success" | "error" | "pending";
}

export interface AdminUpdatesResponse {
  events: IngestionEvent[];
}

export interface HealthResponse {
  status: "healthy" | "unhealthy";
  timestamp: string;
}

// Request Types
export interface RAGQueryRequest {
  question: string;
  top_k: number;
  filters?: {
    source?: string[];
    [key: string]: any;
  };
}

export interface AgentRequest {
  question: string;
  top_k: number;
  model?: string;
}

export interface UploadRequest {
  file: File;
  path: string;
}

// UI State Types
export interface SearchFilters {
  source?: string;
  language?: string;
}

export interface AppConfig {
  apiBaseUrl: string;
  apiKey?: string;
  defaultTopK: number;
  defaultModel?: string;
  confidenceThreshold: number;
}

// Confluence Types
export interface ConfluenceFullSyncRequest {
  space_key?: string;
  root_page_id?: string;
  path_prefix?: string;
  include_labels: string[];
  exclude_labels: string[];
  max_pages: number;
  max_depth: number;
  dry_run: boolean;
}

export interface ConfluenceFullSyncResponse {
  job_id: string;
  status: string;
}

export interface ConfluenceProgress {
  discovered_pages: number;
  fetched_pages: number;
  indexed_chunks: number;
  skipped_unchanged: number;
  failed_pages: number;
}

export interface ConfluenceJobStatus {
  job_id: string;
  status: string;
  progress: ConfluenceProgress;
  current?: {
    page_id: string;
    title: string;
  };
  logs_tail: string[];
  error_message?: string;
  started_at?: string;
  completed_at?: string;
}

export interface ConfluenceCancelRequest {
  job_id: string;
}

export interface ConfluenceReportResponse {
  job_id: string;
  report_type: string;
  total_items: number;
  items: Array<{
    page_id: string;
    title: string;
    error?: string;
    doc_id?: string;
    chunks?: number;
    reason?: string;
    timestamp: string;
  }>;
}
