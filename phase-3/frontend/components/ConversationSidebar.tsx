"use client";

import { formatDistanceToNow } from "date-fns";
import Link from "next/link";
import { usePathname } from "next/navigation";

export interface ConversationSummary {
  id: string;
  created_at: string;
  last_message_at: string;
}

interface ConversationSidebarProps {
  conversations: ConversationSummary[];
  onNewConversation: () => void;
  onDeleteConversation?: (id: string) => Promise<void>;
  isLoading?: boolean;
}

export default function ConversationSidebar({
  conversations,
  onNewConversation,
  onDeleteConversation,
  isLoading = false,
}: ConversationSidebarProps) {
  const pathname = usePathname();

  return (
    <div className="w-80 bg-white border-r border-gray-200 flex flex-col h-full">
      {/* Header */}
      <div className="px-4 py-4 border-b border-gray-200">
        <button
          onClick={onNewConversation}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded-lg font-medium transition-colors duration-200 flex items-center justify-center space-x-2"
        >
          <svg
            className="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          <span>New Conversation</span>
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="p-4 space-y-3">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="animate-pulse bg-gray-200 h-16 rounded-lg"
              ></div>
            ))}
          </div>
        ) : conversations.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            <svg
              className="mx-auto h-12 w-12 text-gray-400 mb-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
            <p className="text-sm">No conversations yet</p>
            <p className="text-xs mt-1">Start a new one above</p>
          </div>
        ) : (
          <div className="p-2 space-y-1">
            {conversations.map((conv) => (
              <ConversationItem
                key={conv.id}
                conversation={conv}
                isActive={pathname?.includes(conv.id) ?? false}
                onDelete={onDeleteConversation}
              />
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-gray-200 text-xs text-gray-500">
        <p>Phase 3: Todo AI Chatbot</p>
        <p className="mt-1">Powered by OpenAI GPT-4</p>
      </div>
    </div>
  );
}

function ConversationItem({
  conversation,
  isActive,
  onDelete,
}: {
  conversation: ConversationSummary;
  isActive: boolean;
  onDelete?: (id: string) => Promise<void>;
}) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const handleDelete = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (!showDeleteConfirm) {
      setShowDeleteConfirm(true);
      return;
    }

    if (!onDelete) return;

    setIsDeleting(true);
    try {
      await onDelete(conversation.id);
    } catch (error) {
      console.error("Failed to delete conversation:", error);
      setShowDeleteConfirm(false);
    } finally {
      setIsDeleting(false);
    }
  };

  const timeAgo = formatDistanceToNow(new Date(conversation.last_message_at), {
    addSuffix: true,
  });

  return (
    <Link
      href={`/chat/${conversation.id}`}
      className={`block px-3 py-3 rounded-lg transition-colors duration-150 group relative ${
        isActive
          ? "bg-blue-50 border border-blue-200"
          : "hover:bg-gray-50 border border-transparent"
      }`}
      onMouseLeave={() => setShowDeleteConfirm(false)}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 truncate">
            Conversation
          </p>
          <p className="text-xs text-gray-500 mt-1">{timeAgo}</p>
        </div>

        {onDelete && (
          <button
            onClick={handleDelete}
            disabled={isDeleting}
            className={`ml-2 p-1 rounded transition-colors ${
              showDeleteConfirm
                ? "bg-red-100 text-red-600 hover:bg-red-200"
                : "text-gray-400 hover:text-red-600 hover:bg-red-50"
            } ${isDeleting ? "opacity-50 cursor-not-allowed" : ""}`}
            title={showDeleteConfirm ? "Click again to confirm" : "Delete"}
          >
            {isDeleting ? (
              <svg
                className="animate-spin h-4 w-4"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
            ) : (
              <svg
                className="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            )}
          </button>
        )}
      </div>
    </Link>
  );
}

// Add missing import
import { useState } from "react";
