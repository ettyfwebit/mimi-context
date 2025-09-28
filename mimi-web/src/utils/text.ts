import type { Chunk } from "@/types/api";

/**
 * Generate a smart snippet from full text around keyword matches
 */
export const generateSnippet = (
  text: string,
  query: string,
  maxLength: number = 250,
): string => {
  if (!text || !query) return text?.slice(0, maxLength) || "";

  const words = query.toLowerCase().split(/\s+/).filter(Boolean);
  const lowerText = text.toLowerCase();

  // Find the best match position
  let bestIndex = 0;
  let bestScore = 0;

  for (let i = 0; i < text.length - maxLength; i += 10) {
    const segment = lowerText.slice(i, i + maxLength);
    const score = words.reduce((acc, word) => {
      return acc + (segment.includes(word) ? 1 : 0);
    }, 0);

    if (score > bestScore) {
      bestScore = score;
      bestIndex = i;
    }
  }

  // Extract snippet with word boundaries
  let start = bestIndex;
  let end = Math.min(bestIndex + maxLength, text.length);

  // Adjust to word boundaries
  if (start > 0) {
    const spaceIndex = text.lastIndexOf(" ", start + 20);
    if (spaceIndex > start) start = spaceIndex + 1;
  }

  if (end < text.length) {
    const spaceIndex = text.indexOf(" ", end - 20);
    if (spaceIndex > 0 && spaceIndex < text.length) end = spaceIndex;
  }

  let snippet = text.slice(start, end).trim();

  // Add ellipsis
  if (start > 0) snippet = "..." + snippet;
  if (end < text.length) snippet = snippet + "...";

  return snippet;
};

/**
 * Highlight keywords in text
 */
export const highlightText = (text: string, query: string): string => {
  if (!query) return text;

  const words = query.split(/\s+/).filter(Boolean);
  let highlightedText = text;

  words.forEach((word) => {
    const regex = new RegExp(`(${escapeRegExp(word)})`, "gi");
    highlightedText = highlightedText.replace(
      regex,
      '<mark class="bg-yellow-200 dark:bg-yellow-800 px-1 rounded">$1</mark>',
    );
  });

  return highlightedText;
};

/**
 * Escape special regex characters
 */
const escapeRegExp = (string: string): string => {
  return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
};

/**
 * Get display text for a chunk (prefer snippet, fallback to generated)
 */
export const getChunkDisplayText = (chunk: Chunk, query: string): string => {
  if (chunk.snippet) {
    return chunk.snippet;
  }

  if (chunk.full_text) {
    return generateSnippet(chunk.full_text, query);
  }

  return "No content available";
};

/**
 * Format file size
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return "0 Bytes";

  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
};

/**
 * Format date for display
 */
export const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  } catch {
    return dateString;
  }
};

/**
 * Check if a string looks like a URL
 */
export const isUrl = (str: string): boolean => {
  try {
    const url = new URL(str);
    return url.protocol === "http:" || url.protocol === "https:";
  } catch {
    return str.startsWith("http://") || str.startsWith("https://");
  }
};

/**
 * Copy text to clipboard
 */
export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    // Fallback for older browsers
    const textArea = document.createElement("textarea");
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
      document.execCommand("copy");
      document.body.removeChild(textArea);
      return true;
    } catch {
      document.body.removeChild(textArea);
      return false;
    }
  }
};

/**
 * Generate citation text
 */
export const generateCitation = (chunk: Chunk): string => {
  return `Source: ${chunk.path} (doc_id: ${chunk.doc_id})`;
};

/**
 * Generate curl example for RAG query
 */
export const generateCurlExample = (
  query: string,
  topK: number,
  apiBaseUrl: string,
  apiKey?: string,
): string => {
  const authHeader = apiKey ? ` -H "Authorization: Bearer ${apiKey}"` : "";

  return `curl -X POST "${apiBaseUrl}/rag/query"${authHeader} \\
  -H "Content-Type: application/json" \\
  -d '{"question":"${query.replace(/"/g, '\\"')}","top_k":${topK}}'`;
};
