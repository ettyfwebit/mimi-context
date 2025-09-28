import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Filter, Clock } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Select } from "@/components/ui/Select";
import { Skeleton } from "@/components/ui/Skeleton";
import { formatDate } from "@/utils/text";
import { apiService } from "@/services/api";
import type { IngestionEvent } from "@/types/api";
import { clsx } from "clsx";

export const EventsTab: React.FC = () => {
  const [statusFilter, setStatusFilter] = useState<string>("");

  const { data, isLoading, error } = useQuery({
    queryKey: ["admin-updates"],
    queryFn: () => apiService.getUpdates({ limit: 100 }),
  });

  const allEvents = data?.events || [];
  const filteredEvents = statusFilter
    ? allEvents.filter((event) => event.status === statusFilter)
    : allEvents;

  const statusCounts = {
    success: allEvents.filter((e) => e.status === "success").length,
    error: allEvents.filter((e) => e.status === "error").length,
    pending: allEvents.filter((e) => e.status === "pending").length,
  };

  const getStatusBadge = (status: IngestionEvent["status"]) => {
    const variants = {
      success: "success" as const,
      error: "danger" as const,
      pending: "warning" as const,
    };
    return (
      <Badge variant={variants[status]} size="sm">
        {status}
      </Badge>
    );
  };

  const statusFilterOptions = [
    { value: "", label: "All statuses" },
    { value: "success", label: `Success (${statusCounts.success})` },
    { value: "error", label: `Error (${statusCounts.error})` },
    { value: "pending", label: `Pending (${statusCounts.pending})` },
  ];

  if (error) {
    return (
      <Card className="text-center py-12">
        <p className="text-red-600 dark:text-red-400">
          Failed to load events:{" "}
          {error instanceof Error ? error.message : "Unknown error"}
        </p>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="text-center">
          <div className="text-2xl font-bold text-green-600 dark:text-green-400">
            {statusCounts.success}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Successful
          </div>
        </Card>

        <Card className="text-center">
          <div className="text-2xl font-bold text-red-600 dark:text-red-400">
            {statusCounts.error}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Errors</div>
        </Card>

        <Card className="text-center">
          <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
            {statusCounts.pending}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Pending
          </div>
        </Card>
      </div>

      {/* Filters */}
      <Card className="bg-gray-50 dark:bg-gray-900">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              options={statusFilterOptions}
              className="w-48 bg-white dark:bg-gray-800"
            />
          </div>

          <div className="text-sm text-gray-500 dark:text-gray-400">
            Showing {filteredEvents.length} of {allEvents.length} events
          </div>
        </div>
      </Card>

      {/* Events timeline */}
      <Card padding="none">
        <div className="max-h-96 overflow-y-auto">
          {isLoading ? (
            <div className="p-6 space-y-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="flex items-center space-x-4">
                  <Skeleton width="3rem" height="1.5rem" />
                  <div className="flex-1">
                    <Skeleton height="1rem" className="mb-1" />
                    <Skeleton height="0.75rem" width="60%" />
                  </div>
                  <Skeleton width="4rem" height="1.5rem" />
                </div>
              ))}
            </div>
          ) : filteredEvents.length === 0 ? (
            <div className="p-12 text-center">
              <Clock className="w-8 h-8 mx-auto mb-2 text-gray-400" />
              <p className="text-gray-500 dark:text-gray-400">
                {statusFilter
                  ? `No ${statusFilter} events found`
                  : "No events found"}
              </p>
            </div>
          ) : (
            <div className="p-6">
              <div className="flow-root">
                <ul className="-mb-8">
                  {filteredEvents.map((event, eventIdx) => (
                    <li key={event.id}>
                      <div className="relative pb-8">
                        {eventIdx !== filteredEvents.length - 1 && (
                          <span
                            className="absolute top-5 left-5 -ml-px h-full w-0.5 bg-gray-200 dark:bg-gray-700"
                            aria-hidden="true"
                          />
                        )}
                        <div className="relative flex items-start space-x-3">
                          {/* Status indicator */}
                          <div className="relative">
                            <div
                              className={clsx([
                                "h-10 w-10 rounded-full flex items-center justify-center ring-8 ring-white dark:ring-gray-800",
                                event.status === "success" && "bg-green-500",
                                event.status === "error" && "bg-red-500",
                                event.status === "pending" && "bg-yellow-500",
                              ])}
                            >
                              {event.status === "success" && (
                                <svg
                                  className="w-5 h-5 text-white"
                                  fill="currentColor"
                                  viewBox="0 0 20 20"
                                >
                                  <path
                                    fillRule="evenodd"
                                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                    clipRule="evenodd"
                                  />
                                </svg>
                              )}
                              {event.status === "error" && (
                                <svg
                                  className="w-5 h-5 text-white"
                                  fill="currentColor"
                                  viewBox="0 0 20 20"
                                >
                                  <path
                                    fillRule="evenodd"
                                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                                    clipRule="evenodd"
                                  />
                                </svg>
                              )}
                              {event.status === "pending" && (
                                <svg
                                  className="w-5 h-5 text-white animate-spin"
                                  fill="none"
                                  viewBox="0 0 24 24"
                                >
                                  <circle
                                    className="opacity-25"
                                    cx="12"
                                    cy="12"
                                    r="10"
                                    stroke="currentColor"
                                    strokeWidth="4"
                                  />
                                  <path
                                    className="opacity-75"
                                    fill="currentColor"
                                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                  />
                                </svg>
                              )}
                            </div>
                          </div>

                          {/* Event content */}
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center justify-between">
                              <div>
                                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                                  {event.type}
                                </p>
                                <p className="text-sm text-gray-500 dark:text-gray-400">
                                  {event.ref}
                                </p>
                              </div>
                              <div className="flex items-center space-x-2">
                                {getStatusBadge(event.status)}
                                <span className="text-xs text-gray-500 dark:text-gray-400">
                                  {formatDate(event.time)}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};
