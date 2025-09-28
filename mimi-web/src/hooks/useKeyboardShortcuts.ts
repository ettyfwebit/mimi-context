import { useEffect } from "react";

interface KeyboardShortcuts {
  onSearch?: () => void;
  onSubmit?: () => void;
}

export const useKeyboardShortcuts = ({
  onSearch,
  onSubmit,
}: KeyboardShortcuts) => {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Focus search on "/"
      if (event.key === "/" && !isInputFocused()) {
        event.preventDefault();
        onSearch?.();
      }

      // Submit on Cmd/Ctrl + Enter
      if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
        event.preventDefault();
        onSubmit?.();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [onSearch, onSubmit]);
};

const isInputFocused = (): boolean => {
  const activeElement = document.activeElement;
  return (
    activeElement instanceof HTMLInputElement ||
    activeElement instanceof HTMLTextAreaElement ||
    activeElement?.getAttribute("contenteditable") === "true"
  );
};
