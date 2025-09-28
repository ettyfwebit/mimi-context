import React from "react";
import { NavLink } from "react-router-dom";
import { Search, MessageSquare, Settings, Moon, Sun } from "lucide-react";
import { useDarkMode } from "@/hooks/useDarkMode";
import { Button } from "@/components/ui/Button";
import { clsx } from "clsx";

interface NavigationProps {
  agentEnabled: boolean;
}

export const Navigation: React.FC<NavigationProps> = ({ agentEnabled }) => {
  const { isDark, toggleDarkMode } = useDarkMode();

  const navItems = [
    { to: "/search", icon: Search, label: "Search" },
    ...(agentEnabled
      ? [{ to: "/chat", icon: MessageSquare, label: "Chat" }]
      : []),
    { to: "/studio", icon: Settings, label: "Studio" },
  ];

  return (
    <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center space-x-8">
            <div className="flex-shrink-0">
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                Mimi Web
              </h1>
            </div>

            <div className="hidden md:flex space-x-4">
              {navItems.map(({ to, icon: Icon, label }) => (
                <NavLink
                  key={to}
                  to={to}
                  className={({ isActive }) =>
                    clsx([
                      "inline-flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors",
                      isActive
                        ? "text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/20"
                        : "text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700",
                    ])
                  }
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {label}
                </NavLink>
              ))}
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleDarkMode}
              aria-label="Toggle dark mode"
            >
              {isDark ? (
                <Sun className="w-4 h-4" />
              ) : (
                <Moon className="w-4 h-4" />
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile navigation */}
      <div className="md:hidden border-t border-gray-200 dark:border-gray-700">
        <div className="px-2 py-3 space-y-1">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                clsx([
                  "flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors",
                  isActive
                    ? "text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/20"
                    : "text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700",
                ])
              }
            >
              <Icon className="w-4 h-4 mr-3" />
              {label}
            </NavLink>
          ))}
        </div>
      </div>
    </nav>
  );
};
