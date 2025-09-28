/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_MIMI_API_BASE: string;
  readonly VITE_MIMI_API_KEY?: string;
  readonly VITE_MIMI_DEFAULT_TOP_K?: string;
  readonly VITE_MIMI_DEFAULT_MODEL?: string;
  readonly VITE_MIMI_CONFIDENCE_THRESHOLD?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
