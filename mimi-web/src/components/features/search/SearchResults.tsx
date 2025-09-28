import React, { useState } from "react";
import {
  ExternalLink,
  Copy,
  ChevronDown,
  ChevronRight,
  AlertTriangle,
} from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import {
  getChunkDisplayText,
  highlightText,
  generateCitation,
  copyToClipboard,
  isUrl,
} from "@/utils/text";
import { config } from "@/utils/config";
import toast from "react-hot-toast";
import { clsx } from "clsx";
import type { Chunk } from "@/types/api";

interface SearchResultsProps {
  chunks: Chunk[];
  query: string;
  loading?: boolean;
}

interface ResultItemProps {
  chunk: Chunk;
  query: string;
  onSelect: (chunk: Chunk) => void;
  isSelected: boolean;
}

const ResultItem: React.FC<ResultItemProps> = ({
  chunk,
  query,
  onSelect,
  isSelected,
}) => {
  const [expanded, setExpanded] = useState(false);
  const displayText = getChunkDisplayText(chunk, query);
  const isLowConfidence = chunk.score < config.confidenceThreshold;

  const handleCopyCitation = async () => {
    const citation = generateCitation(chunk);
    const success = await copyToClipboard(citation);
    if (success) {
      toast.success("Citation copied to clipboard");
    } else {
      toast.error("Failed to copy citation");
    }
  };

  const handleCopyChunk = async () => {
    const text = chunk.full_text || chunk.snippet || displayText;
    const success = await copyToClipboard(text);
    if (success) {
      toast.success("Chunk content copied");
    } else {
      toast.error("Failed to copy content");
    }
  };

  return (
    <Card
      className={clsx([
        "cursor-pointer transition-all duration-200 hover:shadow-md",
        isSelected && "ring-2 ring-primary-500",
        isLowConfidence && "opacity-75",
      ])}
      onClick={() => onSelect(chunk)}
    >
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            {chunk.section_title && (
              <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">
                {chunk.section_title}
              </h3>
            )}
            <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
              <span className="truncate">{chunk.path}</span>
              {isUrl(chunk.path) && (
                <a
                  href={chunk.path}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-shrink-0 p-1 hover:text-gray-700 dark:hover:text-gray-300"
                  onClick={(e) => e.stopPropagation()}
                >
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </div>
          </div>

          <div className="flex items-center space-x-2 ml-4">
            <Badge variant={isLowConfidence ? "warning" : "primary"} size="sm">
              {(chunk.score * 100).toFixed(0)}%
            </Badge>
            {isLowConfidence && (
              <AlertTriangle className="w-4 h-4 text-yellow-500" />
            )}
          </div>
        </div>

        {/* Content */}
        <div
          className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed"
          dangerouslySetInnerHTML={{
            __html: highlightText(displayText, query),
          }}
        />

        {/* Actions */}
        <div className="flex items-center justify-between pt-2 border-t border-gray-100 dark:border-gray-700">
          <div className="flex items-center space-x-2">
            <Badge variant="secondary" size="sm">
              {chunk.source}
            </Badge>
            {chunk.char_start !== undefined && chunk.char_end !== undefined && (
              <span className="text-xs text-gray-500 dark:text-gray-400">
                chars {chunk.char_start}-{chunk.char_end}
              </span>
            )}
          </div>

          <div className="flex items-center space-x-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                handleCopyCitation();
              }}
            >
              <Copy className="w-3 h-3 mr-1" />
              Citation
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                setExpanded(!expanded);
              }}
            >
              {expanded ? (
                <ChevronDown className="w-3 h-3 mr-1" />
              ) : (
                <ChevronRight className="w-3 h-3 mr-1" />
              )}
              Details
            </Button>
          </div>
        </div>

        {/* Expanded details */}
        {expanded && (
          <div className="pt-4 border-t border-gray-100 dark:border-gray-700 space-y-3">
            {chunk.full_text && (
              <div>
                <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
                  Full Text
                </h4>
                <div className="bg-gray-50 dark:bg-gray-900 rounded-md p-3 text-sm text-gray-700 dark:text-gray-300 max-h-64 overflow-y-auto">
                  {chunk.full_text}
                </div>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4 text-xs text-gray-500 dark:text-gray-400">
              <div>
                <span className="font-medium">Document ID:</span>
                <div className="font-mono">{chunk.doc_id}</div>
              </div>
              <div>
                <span className="font-medium">Chunk ID:</span>
                <div className="font-mono">{chunk.chunk_id}</div>
              </div>
            </div>

            <Button
              variant="secondary"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                handleCopyChunk();
              }}
              className="w-full"
            >
              <Copy className="w-3 h-3 mr-1" />
              Copy Full Content
            </Button>
          </div>
        )}
      </div>
    </Card>
  );
};

export const SearchResults: React.FC<SearchResultsProps> = ({
  chunks,
  query,
  loading,
}) => {
  const [selectedChunk, setSelectedChunk] = useState<Chunk | null>(null);
  const lowConfidenceResults = chunks.filter(
    (chunk) => chunk.score < config.confidenceThreshold,
  );
  const showLowConfidenceWarning =
    lowConfidenceResults.length === chunks.length && chunks.length > 0;

  if (loading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <Card key={i} className="animate-pulse">
            <div className="space-y-3">
              <div className="flex justify-between">
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2" />
                <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-12" />
              </div>
              <div className="space-y-2">
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded" />
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-4/5" />
              </div>
              <div className="flex justify-between">
                <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-20" />
                <div className="flex space-x-2">
                  <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-16" />
                  <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-16" />
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    );
  }

  if (chunks.length === 0) {
    return (
      <Card className="text-center py-12">
        <div className="max-w-md mx-auto">
          <div className="w-12 h-12 mx-auto mb-4 text-gray-400">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1}
                d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 20.4c-2.21 0-4.21-.896-5.657-2.343C5.895 16.615 5 14.615 5 12.4s.895-4.215 2.343-5.657A7.962 7.962 0 0112 4.4c2.21 0 4.21.896 5.657 2.343A7.962 7.962 0 0120 12.4v.591"
              />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            No results found
          </h3>
          <p className="text-gray-500 dark:text-gray-400">
            Try rephrasing your query or uploading more documents to improve
            search results.
          </p>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {showLowConfidenceWarning && (
        <Card className="bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                Low Confidence Results
              </h3>
              <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                All results have low confidence scores (&lt;{" "}
                {(config.confidenceThreshold * 100).toFixed(0)}%). Consider
                rephrasing your query or uploading more relevant documents.
              </p>
            </div>
          </div>
        </Card>
      )}

      <div className="text-sm text-gray-600 dark:text-gray-400 mb-4">
        Found {chunks.length} result{chunks.length !== 1 ? "s" : ""} for "
        {query}"
      </div>

      {chunks.map((chunk) => (
        <ResultItem
          key={chunk.chunk_id}
          chunk={chunk}
          query={query}
          onSelect={setSelectedChunk}
          isSelected={selectedChunk?.chunk_id === chunk.chunk_id}
        />
      ))}
    </div>
  );
};
