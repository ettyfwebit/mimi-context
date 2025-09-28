import React, { useState } from "react";
import { StudioTabs } from "@/components/features/studio/StudioTabs";
import { UploadTab } from "@/components/features/studio/UploadTab";
import { DocsTab } from "@/components/features/studio/DocsTab";
import { EventsTab } from "@/components/features/studio/EventsTab";
import { HealthTab } from "@/components/features/studio/HealthTab";
import { ConfluenceSync } from "@/components/features/ConfluenceSync";

type TabId = "upload" | "docs" | "events" | "health" | "confluence";

const tabs = [
  { id: "upload" as TabId, label: "Upload" },
  { id: "docs" as TabId, label: "Documents" },
  { id: "events" as TabId, label: "Events" },
  { id: "health" as TabId, label: "Health" },
  { id: "confluence" as TabId, label: "Confluence Sync" },
];

export const StudioPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabId>("upload");

  const renderTabContent = () => {
    switch (activeTab) {
      case "upload":
        return <UploadTab />;
      case "docs":
        return <DocsTab />;
      case "events":
        return <EventsTab />;
      case "health":
        return <HealthTab />;
      case "confluence":
        return <ConfluenceSync />;
      default:
        return null;
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Studio
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Manage your knowledge base and monitor system health
        </p>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="px-6 pt-6">
          <StudioTabs
            tabs={tabs}
            activeTab={activeTab}
            onTabChange={(tabId) => setActiveTab(tabId as TabId)}
          />
        </div>

        <div className="p-6">{renderTabContent()}</div>
      </div>
    </div>
  );
};
