import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search, Copy, ExternalLink, Filter } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";
import { formatDate, copyToClipboard, isUrl } from "@/utils/text";
import { apiService } from "@/services/api";
import toast from "react-hot-toast";
import type { Document } from "@/types/api";

export const DocsTab: React.FC = () => {
  const [sourceFilter, setSourceFilter] = useState("");
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ["admin-docs", sourceFilter],
    queryFn: () =>
      apiService.getDocuments({
        source: sourceFilter || undefined,
        limit: 50,
      }),
  });

  const documents = data?.documents || [];

  const handleCopyDocId = async (docId: string) => {
    const success = await copyToClipboard(docId);
    if (success) {
      toast.success("Document ID copied to clipboard");
    } else {
      toast.error("Failed to copy to clipboard");
    }
  };

  if (error) {
    return (
      <Card className="text-center py-12">
        <p className="text-red-600 dark:text-red-400">
          Failed to load documents:{" "}
          {error instanceof Error ? error.message : "Unknown error"}
        </p>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <Card className="bg-gray-50 dark:bg-gray-900">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <Input
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value)}
              placeholder="Filter by source..."
              className="bg-white dark:bg-gray-800"
            />
          </div>
          <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
            <Filter className="w-4 h-4 mr-1" />
            {documents.length} document{documents.length !== 1 ? "s" : ""}
          </div>
        </div>
      </Card>

      {/* Documents table */}
      <Card padding="none">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-900/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Document
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Source
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Updated
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Language
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {isLoading ? (
                // Loading skeletons
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i}>
                    <td className="px-6 py-4">
                      <Skeleton height="1.25rem" className="mb-1" />
                      <Skeleton height="0.875rem" width="60%" />
                    </td>
                    <td className="px-6 py-4">
                      <Skeleton height="1rem" width="4rem" />
                    </td>
                    <td className="px-6 py-4">
                      <Skeleton height="1rem" width="6rem" />
                    </td>
                    <td className="px-6 py-4">
                      <Skeleton height="1rem" width="2rem" />
                    </td>
                    <td className="px-6 py-4">
                      <Skeleton height="1.5rem" width="5rem" />
                    </td>
                  </tr>
                ))
              ) : documents.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center">
                    <div className="text-gray-500 dark:text-gray-400">
                      <Search className="w-8 h-8 mx-auto mb-2" />
                      <p>No documents found</p>
                      {sourceFilter && (
                        <p className="text-sm mt-1">
                          Try adjusting your filter or upload some documents
                        </p>
                      )}
                    </div>
                  </td>
                </tr>
              ) : (
                documents.map((doc) => (
                  <tr
                    key={doc.doc_id}
                    className="hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                    onClick={() => setSelectedDoc(doc)}
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-3">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                            {doc.path}
                          </p>
                          <p className="text-xs font-mono text-gray-500 dark:text-gray-400 truncate">
                            {doc.doc_id}
                          </p>
                        </div>
                        {isUrl(doc.path) && (
                          <a
                            href={doc.path}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant="secondary" size="sm">
                        {doc.source}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                      {formatDate(doc.updated_at)}
                    </td>
                    <td className="px-6 py-4">
                      {doc.lang && (
                        <Badge variant="secondary" size="sm">
                          {doc.lang}
                        </Badge>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleCopyDocId(doc.doc_id);
                        }}
                      >
                        <Copy className="w-3 h-3 mr-1" />
                        Copy ID
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Document details panel */}
      {selectedDoc && (
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Document Details
            </h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSelectedDoc(null)}
            >
              ✕
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Document ID
              </h4>
              <div className="flex items-center space-x-2">
                <code className="text-sm bg-gray-100 dark:bg-gray-900 px-2 py-1 rounded">
                  {selectedDoc.doc_id}
                </code>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleCopyDocId(selectedDoc.doc_id)}
                >
                  <Copy className="w-3 h-3" />
                </Button>
              </div>
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Path
              </h4>
              <p className="text-sm text-gray-900 dark:text-gray-100">
                {selectedDoc.path}
              </p>
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Source
              </h4>
              <Badge variant="secondary">{selectedDoc.source}</Badge>
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Last Updated
              </h4>
              <p className="text-sm text-gray-900 dark:text-gray-100">
                {formatDate(selectedDoc.updated_at)}
              </p>
            </div>

            {selectedDoc.lang && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Language
                </h4>
                <Badge variant="secondary">{selectedDoc.lang}</Badge>
              </div>
            )}

            {selectedDoc.hash && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Hash
                </h4>
                <code className="text-xs text-gray-600 dark:text-gray-400">
                  {selectedDoc.hash}
                </code>
              </div>
            )}
          </div>
        </Card>
      )}
    </div>
  );
};
