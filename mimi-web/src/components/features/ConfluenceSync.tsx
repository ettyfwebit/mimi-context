import React, { useState, useEffect } from "react";
import { 
  Play, 
  Square, 
  Loader2, 
  CheckCircle, 
  XCircle, 
  FileText,
  Eye
} from "lucide-react";
import apiService from "@/services/api";
import toast from "react-hot-toast";
import type { 
  ConfluenceFullSyncRequest,
  ConfluenceJobStatus,
  ConfluenceReportResponse 
} from "@/types/api";

interface ConfluenceSyncProps {
  onClose?: () => void;
}

export const ConfluenceSync: React.FC<ConfluenceSyncProps> = ({ onClose }) => {
  const [formData, setFormData] = useState<ConfluenceFullSyncRequest>({
    space_key: "",
    root_page_id: "",
    path_prefix: "",
    include_labels: [],
    exclude_labels: [],
    max_pages: 2000,
    max_depth: 5,
    dry_run: false,
  });

  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<ConfluenceJobStatus | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [showReports, setShowReports] = useState(false);
  const [reports, setReports] = useState<{
    failed?: ConfluenceReportResponse;
    indexed?: ConfluenceReportResponse;
    skipped?: ConfluenceReportResponse;
  }>({});

  // Poll job status
  useEffect(() => {
    if (!currentJobId || !isRunning) return;

    const pollInterval = setInterval(async () => {
      try {
        const status = await apiService.getConfluenceSyncStatus(currentJobId);
        setJobStatus(status);

        // Check if job is complete
        if (["completed", "failed", "cancelled"].includes(status.status)) {
          setIsRunning(false);
          if (status.status === "completed") {
            toast.success("Sync completed successfully!");
            // Fetch reports
            await fetchReports(currentJobId);
          } else if (status.status === "failed") {
            toast.error(`Sync failed: ${status.error_message || "Unknown error"}`);
          } else if (status.status === "cancelled") {
            toast.error("Sync was cancelled");
          }
        }
      } catch (error) {
        console.error("Error polling job status:", error);
        // Don't show toast for polling errors as they may be frequent
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(pollInterval);
  }, [currentJobId, isRunning]);

  const fetchReports = async (jobId: string) => {
    try {
      const [failed, indexed, skipped] = await Promise.all([
        apiService.getConfluenceReport(jobId, "failed").catch(() => null),
        apiService.getConfluenceReport(jobId, "indexed").catch(() => null),
        apiService.getConfluenceReport(jobId, "skipped").catch(() => null),
      ]);

      setReports({
        failed: failed || undefined,
        indexed: indexed || undefined,
        skipped: skipped || undefined,
      });
    } catch (error) {
      console.error("Error fetching reports:", error);
    }
  };

  const handleStart = async () => {
    try {
      // Validate form
      if (!formData.space_key && !formData.root_page_id) {
        toast.error("Please provide either a Space Key or Root Page ID");
        return;
      }

      // Parse labels from comma-separated strings
      const request: ConfluenceFullSyncRequest = {
        ...formData,
        include_labels: formData.include_labels || [],
        exclude_labels: formData.exclude_labels || [],
      };

      const response = await apiService.startConfluenceSync(request);
      setCurrentJobId(response.job_id);
      setIsRunning(true);
      setJobStatus(null);
      setReports({});
      
      toast.success(`Started sync job: ${response.job_id}`);
    } catch (error) {
      console.error("Error starting sync:", error);
      toast.error("Failed to start sync");
    }
  };

  const handleCancel = async () => {
    if (!currentJobId) return;

    try {
      await apiService.cancelConfluenceSync({ job_id: currentJobId });
      toast.success("Sync cancelled");
      setIsRunning(false);
    } catch (error) {
      console.error("Error cancelling sync:", error);
      toast.error("Failed to cancel sync");
    }
  };

  const handleInputChange = (field: keyof ConfluenceFullSyncRequest, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleLabelsChange = (field: "include_labels" | "exclude_labels", value: string) => {
    const labels = value.split(",").map(l => l.trim()).filter(l => l.length > 0);
    handleInputChange(field, labels);
  };

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case "failed":
        return <XCircle className="w-5 h-5 text-red-500" />;
      case "cancelled":
        return <Square className="w-5 h-5 text-gray-500" />;
      default:
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
    }
  };

  const getStatusColor = (status?: string) => {
    switch (status) {
      case "completed":
        return "text-green-600 bg-green-50";
      case "failed":
        return "text-red-600 bg-red-50";
      case "cancelled":
        return "text-gray-600 bg-gray-50";
      default:
        return "text-blue-600 bg-blue-50";
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Confluence Full Sync</h2>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ×
          </button>
        )}
      </div>

      {/* Configuration Form */}
      {!isRunning && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-medium mb-4">Sync Configuration</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Space Key
              </label>
              <input
                type="text"
                value={formData.space_key || ""}
                onChange={(e) => handleInputChange("space_key", e.target.value)}
                placeholder="e.g., ENG"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">Sync entire space</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Root Page ID
              </label>
              <input
                type="text"
                value={formData.root_page_id || ""}
                onChange={(e) => handleInputChange("root_page_id", e.target.value)}
                placeholder="e.g., 123456"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">Alternative to space key</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Include Labels
              </label>
              <input
                type="text"
                value={(formData.include_labels || []).join(", ")}
                onChange={(e) => handleLabelsChange("include_labels", e.target.value)}
                placeholder="e.g., kb, public"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">Comma-separated labels</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Exclude Labels
              </label>
              <input
                type="text"
                value={(formData.exclude_labels || []).join(", ")}
                onChange={(e) => handleLabelsChange("exclude_labels", e.target.value)}
                placeholder="e.g., draft, deprecated"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">Comma-separated labels</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Pages
              </label>
              <input
                type="number"
                value={formData.max_pages}
                onChange={(e) => handleInputChange("max_pages", parseInt(e.target.value) || 2000)}
                min="1"
                max="10000"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Depth
              </label>
              <input
                type="number"
                value={formData.max_depth}
                onChange={(e) => handleInputChange("max_depth", parseInt(e.target.value) || 5)}
                min="1"
                max="20"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="flex items-center mt-4">
            <input
              type="checkbox"
              id="dry_run"
              checked={formData.dry_run}
              onChange={(e) => handleInputChange("dry_run", e.target.checked)}
              className="mr-2"
            />
            <label htmlFor="dry_run" className="text-sm text-gray-700">
              Dry run (discover and analyze only, don't index)
            </label>
          </div>

          <div className="flex justify-end mt-6">
            <button
              onClick={handleStart}
              disabled={isRunning}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              <Play className="w-4 h-4 mr-2" />
              Start Sync
            </button>
          </div>
        </div>
      )}

      {/* Job Status */}
      {jobStatus && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              {getStatusIcon(jobStatus.status)}
              <span className={`ml-2 px-2 py-1 rounded-full text-sm font-medium ${getStatusColor(jobStatus.status)}`}>
                {jobStatus.status.toUpperCase()}
              </span>
            </div>
            <div className="text-sm text-gray-500">
              Job ID: {jobStatus.job_id}
            </div>
          </div>

          {/* Progress */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{jobStatus.progress.discovered_pages}</div>
              <div className="text-sm text-gray-500">Discovered</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{jobStatus.progress.fetched_pages}</div>
              <div className="text-sm text-gray-500">Fetched</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{jobStatus.progress.indexed_chunks}</div>
              <div className="text-sm text-gray-500">Chunks</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">{jobStatus.progress.skipped_unchanged}</div>
              <div className="text-sm text-gray-500">Skipped</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{jobStatus.progress.failed_pages}</div>
              <div className="text-sm text-gray-500">Failed</div>
            </div>
          </div>

          {/* Current Activity */}
          {jobStatus.current && (
            <div className="mb-4 p-3 bg-blue-50 rounded-lg">
              <div className="text-sm font-medium text-blue-900">
                Currently processing: {jobStatus.current.title}
              </div>
              <div className="text-xs text-blue-700">
                Page ID: {jobStatus.current.page_id}
              </div>
            </div>
          )}

          {/* Logs */}
          {jobStatus.logs_tail && jobStatus.logs_tail.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Recent Activity</h4>
              <div className="bg-gray-50 rounded-lg p-3 max-h-32 overflow-y-auto">
                {jobStatus.logs_tail.map((log, index) => (
                  <div key={index} className="text-xs text-gray-600 font-mono">
                    {log}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-between">
            <button
              onClick={() => setShowReports(!showReports)}
              className="flex items-center px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-md"
            >
              <Eye className="w-4 h-4 mr-2" />
              View Reports
            </button>
            
            {isRunning && (
              <button
                onClick={handleCancel}
                className="flex items-center px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                <Square className="w-4 h-4 mr-2" />
                Cancel
              </button>
            )}
          </div>
        </div>
      )}

      {/* Reports */}
      {showReports && (
        <div className="space-y-4">
          {["indexed", "skipped", "failed"].map((type) => {
            const report = reports[type as keyof typeof reports];
            if (!report || report.total_items === 0) return null;

            return (
              <div key={type} className="bg-white rounded-lg border border-gray-200 p-6">
                <h3 className="text-lg font-medium mb-4 capitalize flex items-center">
                  <FileText className="w-5 h-5 mr-2" />
                  {type} Pages ({report.total_items})
                </h3>
                
                <div className="space-y-2">
                  {report.items.slice(0, 10).map((item, index) => (
                    <div key={index} className="flex justify-between items-center p-2 hover:bg-gray-50 rounded">
                      <div>
                        <div className="font-medium">{item.title}</div>
                        <div className="text-sm text-gray-500">{item.page_id}</div>
                        {item.error && (
                          <div className="text-sm text-red-600">{item.error}</div>
                        )}
                        {item.chunks && (
                          <div className="text-sm text-green-600">{item.chunks} chunks</div>
                        )}
                      </div>
                      <div className="text-xs text-gray-400">
                        {new Date(item.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  ))}
                  
                  {report.items.length > 10 && (
                    <div className="text-sm text-gray-500 text-center py-2">
                      ... and {report.items.length - 10} more
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Completion Actions */}
      {jobStatus?.status === "completed" && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
              <span className="text-green-800 font-medium">
                Sync completed successfully! 
                {jobStatus.progress.indexed_chunks > 0 && (
                  <span className="ml-2">
                    {jobStatus.progress.indexed_chunks} chunks indexed.
                  </span>
                )}
              </span>
            </div>
            <button
              onClick={() => {
                // Navigate to search with a sample query
                if (window.location.pathname !== "/search") {
                  window.location.href = "/search?q=refund";
                }
              }}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              Search Now
            </button>
          </div>
        </div>
      )}
    </div>
  );
};