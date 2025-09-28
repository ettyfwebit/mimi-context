import React, { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { AlertCircle, Eye, EyeOff } from 'lucide-react';
import { ChatMessage } from '@/components/features/chat/ChatMessage';
import { ChatComposer } from '@/components/features/chat/ChatComposer';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { apiService } from '@/services/api';
import type { AgentRequest } from '@/types/api';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  sources?: Array<{ doc_id: string; path: string }>;
  timestamp: Date;
  rawChunks?: any[];
}

export const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [showRawChunks, setShowRawChunks] = useState(false);
  const [agentEnabled, setAgentEnabled] = useState<boolean | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Check if agent is available
    apiService.checkAgentAvailability().then(setAgentEnabled);
  }, []);

  const mutation = useMutation({
    mutationFn: (request: AgentRequest) => apiService.askAgent(request),
    onSuccess: (data) => {
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        type: 'assistant',
        content: data.answer,
        sources: data.citations,
        timestamp: new Date(),
        rawChunks: data.raw_chunks,
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    },
    onError: (error) => {
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        type: 'assistant',
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorMessage]);
    },
  });

  const handleSendMessage = (data: { question: string; top_k: number; model?: string }) => {
    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: data.question,
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    
    // Send to agent
    mutation.mutate(data);
  };

  if (agentEnabled === null) {
    return (
      <div className="max-w-4xl mx-auto">
        <Card className="text-center py-12">
          <div className="animate-spin w-8 h-8 mx-auto mb-4 border-2 border-primary-600 border-t-transparent rounded-full" />
          <p className="text-gray-600 dark:text-gray-400">
            Checking agent availability...
          </p>
        </Card>
      </div>
    );
  }

  if (agentEnabled === false) {
    return (
      <div className="max-w-4xl mx-auto">
        <Card className="text-center py-12">
          <AlertCircle className="w-12 h-12 mx-auto mb-4 text-yellow-500" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            Agent Not Available
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            The chat agent is not enabled or not responding. Please use the Search feature instead.
          </p>
          <Button
            onClick={() => window.location.href = '/search'}
            variant="primary"
          >
            Go to Search
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Chat with Agent
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Ask questions and get intelligent answers with source citations
        </p>
      </div>

      {/* Developer toggle */}
      <div className="flex justify-end">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowRawChunks(!showRawChunks)}
          className="text-xs"
        >
          {showRawChunks ? (
            <EyeOff className="w-3 h-3 mr-1" />
          ) : (
            <Eye className="w-3 h-3 mr-1" />
          )}
          {showRawChunks ? 'Hide' : 'Show'} raw chunks
        </Button>
      </div>

      {/* Messages */}
      <div className="space-y-6 min-h-[400px] max-h-[600px] overflow-y-auto">
        {messages.length === 0 && (
          <Card className="text-center py-12">
            <div className="w-16 h-16 mx-auto mb-4 text-gray-400">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
              Start a conversation
            </h3>
            <p className="text-gray-500 dark:text-gray-400">
              Ask a question to get started with the AI agent
            </p>
          </Card>
        )}

        {messages.map((message) => (
          <div key={message.id}>
            <ChatMessage
              type={message.type}
              content={message.content}
              sources={message.sources}
              timestamp={message.timestamp}
            />
            
            {/* Raw chunks debug view */}
            {showRawChunks && message.rawChunks && message.rawChunks.length > 0 && (
              <Card className="mt-2 bg-gray-50 dark:bg-gray-900 border-gray-200 dark:border-gray-800">
                <h4 className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Raw Chunks (Debug)
                </h4>
                <pre className="text-xs text-gray-600 dark:text-gray-400 overflow-x-auto">
                  {JSON.stringify(message.rawChunks, null, 2)}
                </pre>
              </Card>
            )}
          </div>
        ))}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Composer */}
      <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
        <ChatComposer
          onSubmit={handleSendMessage}
          loading={mutation.isLoading}
          disabled={mutation.isLoading}
        />
      </div>
    </div>
  );
};
