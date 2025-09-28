import React from 'react';
import { Send } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { Button } from '@/components/ui/Button';
import { Select } from '@/components/ui/Select';
import { config } from '@/utils/config';

interface ChatComposerProps {
  onSubmit: (data: { question: string; top_k: number; model?: string }) => void;
  loading?: boolean;
  disabled?: boolean;
}

interface FormData {
  question: string;
  top_k: number;
  model?: string;
}

export const ChatComposer: React.FC<ChatComposerProps> = ({
  onSubmit,
  loading = false,
  disabled = false,
}) => {
  const { register, handleSubmit, reset, watch } = useForm<FormData>({
    defaultValues: {
      question: '',
      top_k: config.defaultTopK,
      model: config.defaultModel || '',
    },
  });

  const question = watch('question');

  const handleFormSubmit = (data: FormData) => {
    onSubmit({
      ...data,
      model: data.model || undefined,
    });
    reset({ question: '', top_k: data.top_k, model: data.model });
  };

  const topKOptions = [
    { value: '3', label: '3 sources' },
    { value: '5', label: '5 sources' },
    { value: '8', label: '8 sources' },
  ];

  const modelOptions = [
    { value: '', label: 'Default model' },
    { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
    { value: 'gpt-4', label: 'GPT-4' },
    { value: 'claude-3-sonnet', label: 'Claude 3 Sonnet' },
  ];

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-2">
        <Select
          {...register('top_k', { valueAsNumber: true })}
          options={topKOptions}
          className="w-full sm:w-32"
        />
        
        {config.defaultModel && (
          <Select
            {...register('model')}
            options={modelOptions}
            className="w-full sm:w-48"
          />
        )}
      </div>

      <div className="flex gap-2">
        <textarea
          {...register('question', { required: true })}
          placeholder="Ask a question about your knowledge base..."
          className="flex-1 min-h-[60px] max-h-32 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md resize-y bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          disabled={disabled || loading}
          onKeyDown={(e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
              e.preventDefault();
              handleSubmit(handleFormSubmit)();
            }
          }}
        />
        
        <Button
          type="submit"
          loading={loading}
          disabled={disabled || !question.trim()}
          className="self-end px-4 py-3"
        >
          <Send className="w-4 h-4" />
        </Button>
      </div>

      <div className="text-xs text-gray-500 dark:text-gray-400">
        <span className="font-medium">Tip:</span> Press{' '}
        <kbd className="px-1 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-xs">
          ⌘+Enter
        </kbd>{' '}
        to send
      </div>
    </form>
  );
};
