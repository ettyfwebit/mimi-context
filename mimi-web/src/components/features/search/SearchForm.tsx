import { useRef, forwardRef, useImperativeHandle } from "react";
import { Search, Copy } from "lucide-react";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { config } from "@/utils/config";
import { generateCurlExample, copyToClipboard } from "@/utils/text";
import toast from "react-hot-toast";

interface SearchFormData {
  question: string;
  top_k: number;
  source?: string;
}

interface SearchFormProps {
  onSubmit: (data: SearchFormData) => void;
  loading?: boolean;
  onFocus?: () => void;
}

export interface SearchFormHandle {
  focus: () => void;
}

export const SearchForm = forwardRef<SearchFormHandle, SearchFormProps>(
  ({ onSubmit, loading = false, onFocus }, ref) => {
    const searchInputRef = useRef<HTMLInputElement>(null);

    const { register, handleSubmit, watch } = useForm<SearchFormData>({
      defaultValues: {
        question: "",
        top_k: config.defaultTopK,
        source: "",
      },
    });

    const question = watch("question");
    const topK = watch("top_k");

    const handleFormSubmit = (data: SearchFormData) => {
      onSubmit({
        ...data,
        source: data.source || undefined,
      });
    };

    const handleCopyCurl = async () => {
      if (!question.trim()) {
        toast.error("Enter a search query first");
        return;
      }

      const curlExample = generateCurlExample(
        question,
        topK,
        config.apiBaseUrl,
        config.apiKey,
      );

      const success = await copyToClipboard(curlExample);
      if (success) {
        toast.success("Curl example copied to clipboard");
      } else {
        toast.error("Failed to copy to clipboard");
      }
    };

    const focusSearchInput = () => {
      searchInputRef.current?.focus();
      onFocus?.();
    };

    // Expose focus method for keyboard shortcuts
    useImperativeHandle(ref, () => ({
      focus: focusSearchInput,
    }));

    const topKOptions = [
      { value: "3", label: "3 results" },
      { value: "5", label: "5 results" },
      { value: "8", label: "8 results" },
    ];

    return (
      <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <Input
              {...register("question", { required: true })}
              ref={searchInputRef}
              placeholder="Ask anything about your knowledge base..."
              className="text-lg"
              onFocus={onFocus}
            />
          </div>

          <div className="flex gap-2">
            <Select
              {...register("top_k", { valueAsNumber: true })}
              options={topKOptions}
              className="w-32"
            />

            <Button
              type="submit"
              loading={loading}
              disabled={!question.trim()}
              className="px-6"
            >
              <Search className="w-4 h-4 mr-2" />
              Search
            </Button>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <Input
              {...register("source")}
              placeholder="Filter by source (optional)"
              helperText="e.g., 'uploads', 'documents'"
            />
          </div>

          <div className="flex items-end">
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleCopyCurl}
              className="whitespace-nowrap"
            >
              <Copy className="w-4 h-4 mr-1" />
              Copy cURL
            </Button>
          </div>
        </div>

        <div className="text-xs text-gray-500 dark:text-gray-400">
          <span className="font-medium">Tip:</span> Press{" "}
          <kbd className="px-1 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-xs">
            /
          </kbd>{" "}
          to focus search,
          <kbd className="px-1 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-xs ml-1">
            ⌘+Enter
          </kbd>{" "}
          to submit
        </div>
      </form>
    );
  },
);

SearchForm.displayName = "SearchForm";
