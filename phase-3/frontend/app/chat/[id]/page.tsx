"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import ChatInterface from "@/components/ChatInterface";
import ConversationSidebar, {
  ConversationSummary,
} from "@/components/ConversationSidebar";
import { apiClient } from "@/lib/api-client";
import { useAuth } from "@/lib/auth-context";
import type { Message } from "@/components/ChatInterface";

export default function ConversationPage() {
  const params = useParams();
  const conversationId = params?.id as string;

  const [messages, setMessages] = useState<Message[]>([]);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingConversations, setIsLoadingConversations] = useState(false);
  const [isLoadingMessages, setIsLoadingMessages] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, authLoading, router]);

  // Load conversation messages
  useEffect(() => {
    if (isAuthenticated && conversationId) {
      loadConversation();
    }
  }, [isAuthenticated, conversationId]);

  // Load conversations list
  useEffect(() => {
    if (isAuthenticated) {
      loadConversations();
    }
  }, [isAuthenticated]);

  const loadConversation = async () => {
    setIsLoadingMessages(true);
    setError(null);

    try {
      const detail = await apiClient.getConversationDetail(conversationId);

      // Transform messages to component format
      const transformedMessages: Message[] = detail.messages.map((msg) => ({
        id: msg.id,
        role: msg.role,
        content: msg.content,
        created_at: msg.created_at,
      }));

      setMessages(transformedMessages);
    } catch (error: any) {
      console.error("Failed to load conversation:", error);
      setError(
        error.detail || "Failed to load conversation. It may have been deleted."
      );
    } finally {
      setIsLoadingMessages(false);
    }
  };

  const loadConversations = async () => {
    setIsLoadingConversations(true);
    try {
      const response = await apiClient.getConversations();
      setConversations(response.conversations);
    } catch (error) {
      console.error("Failed to load conversations:", error);
    } finally {
      setIsLoadingConversations(false);
    }
  };

  const handleSendMessage = async (content: string) => {
    setIsLoading(true);

    try {
      const response = await apiClient.sendMessage({
        message: content,
        conversation_id: conversationId,
      });

      // Add assistant message
      const assistantMessage: Message = {
        id: response.assistant_message_id,
        role: "assistant",
        content: response.message,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Failed to send message:", error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewConversation = () => {
    router.push("/");
  };

  const handleDeleteConversation = async (id: string) => {
    try {
      await apiClient.deleteConversation(id);

      // Remove from local state
      setConversations((prev) => prev.filter((conv) => conv.id !== id));

      // If deleting current conversation, redirect to home
      if (id === conversationId) {
        router.push("/");
      }
    } catch (error) {
      console.error("Failed to delete conversation:", error);
      throw error;
    }
  };

  if (authLoading || isLoadingMessages) {
    return (
      <div className="flex h-screen">
        <ConversationSidebar
          conversations={conversations}
          onNewConversation={handleNewConversation}
          onDeleteConversation={handleDeleteConversation}
          isLoading={isLoadingConversations}
        />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading conversation...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen">
        <ConversationSidebar
          conversations={conversations}
          onNewConversation={handleNewConversation}
          onDeleteConversation={handleDeleteConversation}
          isLoading={isLoadingConversations}
        />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <svg
              className="mx-auto h-12 w-12 text-red-400 mb-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <p className="text-lg font-medium text-gray-900">{error}</p>
            <button
              onClick={handleNewConversation}
              className="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors"
            >
              Start New Conversation
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect to login
  }

  return (
    <div className="flex h-screen">
      <ConversationSidebar
        conversations={conversations}
        onNewConversation={handleNewConversation}
        onDeleteConversation={handleDeleteConversation}
        isLoading={isLoadingConversations}
      />
      <main className="flex-1">
        <ChatInterface
          conversationId={conversationId}
          initialMessages={messages}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      </main>
    </div>
  );
}
