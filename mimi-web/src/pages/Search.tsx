import React, { useState, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  SearchForm,
  SearchFormHandle,
} from "@/components/features/search/SearchForm";
import { SearchResults } from "@/components/features/search/SearchResults";
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts";
import { apiService } from "@/services/api";
import type { RAGQueryRequest, Chunk } from "@/types/api";

interface SearchState {
  query: RAGQueryRequest | null;
  hasSearched: boolean;
}

export const SearchPage: React.FC = () => {
  const [searchState, setSearchState] = useState<SearchState>({
    query: null,
    hasSearched: false,
  });

  const searchFormRef = useRef<SearchFormHandle>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ["search", searchState.query],
    queryFn: () => apiService.queryRAG(searchState.query!),
    enabled: !!searchState.query,
    keepPreviousData: true,
  });

  const handleSearch = (formData: any) => {
    const query: RAGQueryRequest = {
      question: formData.question,
      top_k: formData.top_k,
      filters: formData.source ? { source: [formData.source] } : undefined,
    };

    setSearchState({
      query,
      hasSearched: true,
    });
  };

  const handleFocusSearch = () => {
    searchFormRef.current?.focus();
  };

  useKeyboardShortcuts({
    onSearch: handleFocusSearch,
    onSubmit: () => {
      // Submit will be handled by the form
    },
  });

  const chunks: Chunk[] = data?.chunks || [];
  const currentQuery = searchState.query?.question || "";

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Search Knowledge Base
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Find information quickly with intelligent search and citations
        </p>
      </div>

      <SearchForm
        ref={searchFormRef}
        onSubmit={handleSearch}
        loading={isLoading}
        onFocus={handleFocusSearch}
      />

      {error ? (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
            Search Error
          </h3>
          <p className="text-sm text-red-700 dark:text-red-300 mt-1">
            {error instanceof Error ? error.message : String(error)}
          </p>
        </div>
      ) : null}

      {searchState.hasSearched && (
        <SearchResults
          chunks={chunks}
          query={currentQuery}
          loading={isLoading}
        />
      )}

      {!searchState.hasSearched && (
        <div className="text-center py-12">
          <div className="w-16 h-16 mx-auto mb-4 text-gray-400">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            Ready to search
          </h3>
          <p className="text-gray-500 dark:text-gray-400">
            Enter a question above to search your knowledge base
          </p>
        </div>
      )}
    </div>
  );
};
