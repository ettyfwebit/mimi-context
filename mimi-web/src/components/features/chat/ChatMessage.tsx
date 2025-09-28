import React from 'react';
import { User, Bot, ExternalLink } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { isUrl } from '@/utils/text';
import { clsx } from 'clsx';

interface ChatMessageProps {
  type: 'user' | 'assistant';
  content: string;
  sources?: Array<{ doc_id: string; path: string }>;
  timestamp: Date;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  type,
  content,
  sources,
  timestamp,
}) => {
  const isUser = type === 'user';

  // Parse citation markers [n] and replace with clickable links
  const parsedContent = React.useMemo(() => {
    if (!sources || sources.length === 0) return content;
    
    return content.replace(/\[(\d+)\]/g, (match, num) => {
      const index = parseInt(num, 10) - 1;
      if (index >= 0 && index < sources.length) {
        return `<span class="citation-marker" data-index="${index}">${match}</span>`;
      }
      return match;
    });
  }, [content, sources]);

  const handleCitationClick = (index: number) => {
    if (sources && sources[index]) {
      const source = sources[index];
      // You could implement a modal or side panel to show source details
      console.log('Citation clicked:', source);
    }
  };

  return (
    <div
      className={clsx([
        'flex gap-4',
        isUser ? 'justify-end' : 'justify-start',
      ])}
    >
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
          <Bot className="w-4 h-4 text-primary-600 dark:text-primary-400" />
        </div>
      )}
      
      <div className={clsx(['max-w-3xl', isUser && 'order-first'])}>
        <Card
          className={clsx([
            'text-sm',
            isUser
              ? 'bg-primary-600 text-white border-primary-600'
              : 'bg-white dark:bg-gray-800',
          ])}
        >
          <div
            className="prose prose-sm max-w-none"
            dangerouslySetInnerHTML={{ __html: parsedContent }}
            onClick={(e) => {
              const target = e.target as HTMLElement;
              if (target.classList.contains('citation-marker')) {
                const index = parseInt(target.dataset.index || '0', 10);
                handleCitationClick(index);
              }
            }}
          />
          
          <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100 dark:border-gray-700 text-xs">
            <span className={clsx([
              isUser
                ? 'text-primary-200'
                : 'text-gray-500 dark:text-gray-400'
            ])}>
              {timestamp.toLocaleTimeString()}
            </span>
          </div>
        </Card>

        {/* Sources panel for assistant messages */}
        {!isUser && sources && sources.length > 0 && (
          <div className="mt-3">
            <h4 className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
              Sources
            </h4>
            <div className="space-y-1">
              {sources.map((source, index) => (
                <div
                  key={`${source.doc_id}-${index}`}
                  className="flex items-center space-x-2 text-xs"
                >
                  <Badge variant="secondary" size="sm">
                    [{index + 1}]
                  </Badge>
                  <span className="text-gray-600 dark:text-gray-400 truncate">
                    {source.path}
                  </span>
                  {isUrl(source.path) && (
                    <a
                      href={source.path}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-shrink-0 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                    >
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center">
          <User className="w-4 h-4 text-gray-600 dark:text-gray-400" />
        </div>
      )}
    </div>
  );
};
