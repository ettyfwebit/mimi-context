import React from "react";
import { clsx } from "clsx";

interface Tab {
  id: string;
  label: string;
  count?: number;
}

interface StudioTabsProps {
  tabs: Tab[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
}

export const StudioTabs: React.FC<StudioTabsProps> = ({
  tabs,
  activeTab,
  onTabChange,
}) => {
  return (
    <div className="border-b border-gray-200 dark:border-gray-700">
      <nav className="flex space-x-8" aria-label="Tabs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={clsx([
              "whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm transition-colors",
              activeTab === tab.id
                ? "border-primary-500 text-primary-600 dark:text-primary-400"
                : "border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 hover:border-gray-300",
            ])}
          >
            {tab.label}
            {tab.count !== undefined && (
              <span
                className={clsx([
                  "ml-2 py-0.5 px-2 rounded-full text-xs",
                  activeTab === tab.id
                    ? "bg-primary-100 text-primary-600 dark:bg-primary-900 dark:text-primary-400"
                    : "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400",
                ])}
              >
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </nav>
    </div>
  );
};
