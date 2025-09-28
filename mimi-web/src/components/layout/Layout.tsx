import React, { useEffect, useState } from "react";
import { Outlet } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";
import { Navigation } from "./Navigation";
import { apiService } from "@/services/api";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export const Layout: React.FC = () => {
  const [agentEnabled, setAgentEnabled] = useState(false);

  useEffect(() => {
    // Check if agent endpoint is available
    apiService.checkAgentAvailability().then(setAgentEnabled);
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Navigation agentEnabled={agentEnabled} />
        <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <Outlet />
        </main>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            className: "dark:bg-gray-800 dark:text-white",
          }}
        />
      </div>
    </QueryClientProvider>
  );
};
