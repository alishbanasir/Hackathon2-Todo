"use client";

import { useState } from "react";
import MessageList from "./MessageList";
import MessageInput from "./MessageInput";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

interface ChatInterfaceProps {
  conversationId?: string;
  initialMessages?: Message[];
  onSendMessage: (message: string) => Promise<void>;
  isLoading?: boolean;
}

export default function ChatInterface({
  conversationId,
  initialMessages = [],
  onSendMessage,
  isLoading = false,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [isSending, setIsSending] = useState(false);

  const handleSend = async (content: string) => {
    // Optimistically add user message
    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      role: "user",
      content,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsSending(true);

    try {
      await onSendMessage(content);
      // The parent component will handle adding the assistant's response
    } catch (error) {
      console.error("Failed to send message:", error);
      // Remove optimistic message on error
      setMessages((prev) => prev.filter((msg) => msg.id !== userMessage.id));
      throw error;
    } finally {
      setIsSending(false);
    }
  };

  // Update messages when initialMessages changes (for assistant responses)
  useState(() => {
    if (initialMessages.length > messages.length) {
      setMessages(initialMessages);
    }
  });

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <h1 className="text-xl font-semibold text-gray-900">
          Todo AI Assistant
        </h1>
        {conversationId && (
          <p className="text-sm text-gray-500 mt-1">
            Conversation ID: {conversationId.slice(0, 8)}...
          </p>
        )}
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-hidden">
        <MessageList messages={messages} isLoading={isLoading || isSending} />
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 px-6 py-4">
        <MessageInput onSend={handleSend} disabled={isSending || isLoading} />
      </div>
    </div>
  );
}
