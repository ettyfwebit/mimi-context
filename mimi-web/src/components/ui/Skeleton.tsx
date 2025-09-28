import React from "react";
import { clsx } from "clsx";

interface SkeletonProps {
  className?: string;
  width?: string;
  height?: string;
  lines?: number;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className,
  width,
  height,
  lines = 1,
}) => {
  if (lines > 1) {
    return (
      <div className="space-y-2">
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className={clsx([
              "animate-pulse bg-gray-200 dark:bg-gray-700 rounded",
              i === lines - 1 ? "w-3/4" : "w-full",
              className,
            ])}
            style={{
              width: i === lines - 1 ? "75%" : width,
              height: height || "1rem",
            }}
          />
        ))}
      </div>
    );
  }

  return (
    <div
      className={clsx([
        "animate-pulse bg-gray-200 dark:bg-gray-700 rounded",
        className,
      ])}
      style={{ width, height: height || "1rem" }}
    />
  );
};

export const SkeletonCard: React.FC = () => (
  <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
    <div className="space-y-4">
      <Skeleton height="1.5rem" width="60%" />
      <Skeleton lines={3} />
      <div className="flex space-x-4">
        <Skeleton width="4rem" height="1.25rem" />
        <Skeleton width="3rem" height="1.25rem" />
      </div>
    </div>
  </div>
);
