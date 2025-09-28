import React from "react";
import { useQuery } from "@tanstack/react-query";
import {
  CheckCircle,
  XCircle,
  AlertCircle,
  RefreshCw,
  Eye,
  EyeOff,
} from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { formatDate } from "@/utils/text";
import { config } from "@/utils/config";
import { apiService } from "@/services/api";

export const HealthTab: React.FC = () => {
  const [showApiKey, setShowApiKey] = React.useState(false);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["health"],
    queryFn: () => apiService.getHealth(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  const isHealthy = data?.status === "healthy";

  return (
    <div className="space-y-6">
      {/* Health Status Card */}
      <Card>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Backend Health Status
          </h2>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => refetch()}
            disabled={isLoading}
          >
            <RefreshCw
              className={`w-4 h-4 mr-1 ${isLoading ? "animate-spin" : ""}`}
            />
            Refresh
          </Button>
        </div>

        {error ? (
          <div className="flex items-center space-x-3 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <XCircle className="w-6 h-6 text-red-600 dark:text-red-400 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-red-800 dark:text-red-200">
                Connection Failed
              </p>
              <p className="text-sm text-red-700 dark:text-red-300">
                {error instanceof Error
                  ? error.message
                  : "Unable to connect to backend"}
              </p>
            </div>
          </div>
        ) : isLoading ? (
          <div className="flex items-center space-x-3 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
            <AlertCircle className="w-6 h-6 text-yellow-600 dark:text-yellow-400 flex-shrink-0 animate-pulse" />
            <div>
              <p className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                Checking Status...
              </p>
            </div>
          </div>
        ) : (
          <div
            className={`flex items-center space-x-3 p-4 border rounded-lg ${
              isHealthy
                ? "bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800"
                : "bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800"
            }`}
          >
            {isHealthy ? (
              <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400 flex-shrink-0" />
            ) : (
              <XCircle className="w-6 h-6 text-red-600 dark:text-red-400 flex-shrink-0" />
            )}
            <div className="flex-1">
              <p
                className={`text-sm font-medium ${
                  isHealthy
                    ? "text-green-800 dark:text-green-200"
                    : "text-red-800 dark:text-red-200"
                }`}
              >
                Backend is {isHealthy ? "Healthy" : "Unhealthy"}
              </p>
              {data?.timestamp && (
                <p
                  className={`text-sm ${
                    isHealthy
                      ? "text-green-700 dark:text-green-300"
                      : "text-red-700 dark:text-red-300"
                  }`}
                >
                  Last checked: {formatDate(data.timestamp)}
                </p>
              )}
            </div>
            <Badge variant={isHealthy ? "success" : "danger"} size="sm">
              {data?.status || "Unknown"}
            </Badge>
          </div>
        )}
      </Card>

      {/* Configuration */}
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Configuration
        </h3>

        <div className="space-y-4">
          <div>
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Backend Base URL
            </h4>
            <div className="flex items-center space-x-2">
              <code className="text-sm bg-gray-100 dark:bg-gray-900 px-3 py-1 rounded font-mono">
                {config.apiBaseUrl}
              </code>
              <Badge
                variant={
                  config.apiBaseUrl.includes("localhost")
                    ? "warning"
                    : "primary"
                }
                size="sm"
              >
                {config.apiBaseUrl.includes("localhost") ? "Local" : "Remote"}
              </Badge>
            </div>
          </div>

          <div>
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Authentication
            </h4>
            <div className="flex items-center space-x-2">
              {config.apiKey ? (
                <>
                  <div className="flex items-center space-x-2">
                    <code className="text-sm bg-gray-100 dark:bg-gray-900 px-3 py-1 rounded font-mono">
                      {showApiKey ? config.apiKey : "••••••••••••••••"}
                    </code>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowApiKey(!showApiKey)}
                    >
                      {showApiKey ? (
                        <EyeOff className="w-3 h-3" />
                      ) : (
                        <Eye className="w-3 h-3" />
                      )}
                    </Button>
                  </div>
                  <Badge variant="success" size="sm">
                    Configured
                  </Badge>
                </>
              ) : (
                <>
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    No API key configured
                  </span>
                  <Badge variant="warning" size="sm">
                    Optional
                  </Badge>
                </>
              )}
            </div>
          </div>

          <div>
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Default Settings
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-600 dark:text-gray-400">Top K:</span>
                <span className="ml-2 font-mono">{config.defaultTopK}</span>
              </div>
              <div>
                <span className="text-gray-600 dark:text-gray-400">
                  Confidence Threshold:
                </span>
                <span className="ml-2 font-mono">
                  {(config.confidenceThreshold * 100).toFixed(0)}%
                </span>
              </div>
              {config.defaultModel && (
                <div className="sm:col-span-2">
                  <span className="text-gray-600 dark:text-gray-400">
                    Default Model:
                  </span>
                  <span className="ml-2 font-mono">{config.defaultModel}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </Card>

      {/* Environment Variables Guide */}
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Environment Variables
        </h3>

        <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Required Configuration
          </h4>
          <div className="space-y-2 text-sm font-mono">
            <div>
              <span className="text-blue-600 dark:text-blue-400">
                VITE_MIMI_API_BASE
              </span>
              <span className="text-gray-500 mx-2">=</span>
              <span className="text-green-600 dark:text-green-400">
                http://localhost:8080
              </span>
            </div>
          </div>

          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 mt-4">
            Optional Configuration
          </h4>
          <div className="space-y-2 text-sm font-mono">
            <div>
              <span className="text-blue-600 dark:text-blue-400">
                VITE_MIMI_API_KEY
              </span>
              <span className="text-gray-500 mx-2">=</span>
              <span className="text-gray-400 dark:text-gray-500">
                your-api-key
              </span>
            </div>
            <div>
              <span className="text-blue-600 dark:text-blue-400">
                VITE_MIMI_DEFAULT_TOP_K
              </span>
              <span className="text-gray-500 mx-2">=</span>
              <span className="text-gray-400 dark:text-gray-500">5</span>
            </div>
            <div>
              <span className="text-blue-600 dark:text-blue-400">
                VITE_MIMI_DEFAULT_MODEL
              </span>
              <span className="text-gray-500 mx-2">=</span>
              <span className="text-gray-400 dark:text-gray-500">
                gpt-3.5-turbo
              </span>
            </div>
            <div>
              <span className="text-blue-600 dark:text-blue-400">
                VITE_MIMI_CONFIDENCE_THRESHOLD
              </span>
              <span className="text-gray-500 mx-2">=</span>
              <span className="text-gray-400 dark:text-gray-500">0.30</span>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};
