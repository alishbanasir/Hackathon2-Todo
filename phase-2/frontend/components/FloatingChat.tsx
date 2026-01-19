"use client";

import { useState, useRef, useEffect } from "react";

// Phase 3 AI Chatbot API URL
// FloatingChat.tsx mein localhost hata kar ye dalen:
// FloatingChat.tsx (Line 7)
const AI_CHAT_API = "https://alishba-nasir-todo-api-backend.hf.space/chat";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
}

interface ChatResponse {
  conversation_id: string;
  message: string;
  assistant_message_id: string;
}

export default function FloatingChat() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
    }
  }, [isOpen]);

  // Get auth token from localStorage
  const getAuthToken = (): string | null => {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("auth_token");
  };

  const handleSend = async () => {
    const content = inputValue.trim();
    if (!content || isLoading) return;

    const token = getAuthToken();
    if (!token) {
      setError("Please log in to use the AI assistant");
      return;
    }

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content,
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(AI_CHAT_API, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: content,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Error: ${response.status}`);
      }

      const data: ChatResponse = await response.json();

      const assistantMessage: ChatMessage = {
        id: data.assistant_message_id,
        role: "assistant",
        content: data.message,
      };
      setMessages((prev) => [...prev, assistantMessage]);

      if (!conversationId) {
        setConversationId(data.conversation_id);
      }
    } catch (err) {
      console.error("Chat error:", err);
      setError("AI Service connection issue (Port 8008)");
      setMessages((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          role: "assistant",
          content: "Sorry, I'm having trouble connecting to my brain. Please ensure the Phase-3 backend is running.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setConversationId(undefined);
    setError(null);
  };

  return (
    <>
      {/* Chat Window - Professional Dark Mode */}
      <div
        className={`fixed bottom-24 right-6 w-[380px] bg-zinc-950 rounded-2xl shadow-2xl shadow-black/90 z-[999] overflow-hidden border border-zinc-800/60 transition-all duration-300 ease-out transform ${
          isOpen
            ? "opacity-100 translate-y-0 scale-100"
            : "opacity-0 translate-y-4 scale-95 pointer-events-none"
        }`}
        style={{ maxHeight: "520px" }}
      >
        {/* Header - Consistent with Dashboard */}
        <div className="bg-zinc-900 px-4 py-4 flex items-center justify-between border-b border-zinc-800">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-zinc-800 rounded-lg flex items-center justify-center border border-zinc-700 shadow-inner">
              <svg className="w-5 h-5 text-zinc-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <div>
              <h3 className="text-zinc-100 font-bold text-sm tracking-tight">AI TASK ASSISTANT</h3>
              <div className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
                <p className="text-zinc-500 text-[10px] uppercase font-bold tracking-widest">Active</p>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <button onClick={handleNewChat} className="p-2 text-zinc-500 hover:text-zinc-100 transition-colors" title="Refresh Chat">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
            <button onClick={() => setIsOpen(false)} className="p-2 text-zinc-500 hover:text-white transition-colors">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-950/20 border-b border-red-900/30 px-4 py-2">
            <p className="text-red-400 text-[10px] font-medium">{error}</p>
          </div>
        )}

        {/* Messages Area - Matches both styles */}
        <div className="h-[350px] overflow-y-auto p-4 space-y-4 bg-zinc-950 custom-scrollbar">
          {messages.length === 0 ? (
            <div className="text-center py-20">
              <p className="text-zinc-600 text-xs italic font-medium">Ready to help you manage your tasks...</p>
            </div>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[85%] px-4 py-3 rounded-2xl text-[13px] leading-relaxed shadow-sm border ${
                    msg.role === "user"
                      ? "bg-zinc-800 text-zinc-100 border-zinc-700 rounded-tr-none"
                      : "bg-zinc-800/50 text-zinc-300 border-zinc-800 rounded-tl-none"
                  }`}>
                  {msg.content}
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-zinc-800/30 px-4 py-3 rounded-2xl border border-zinc-800 flex gap-1">
                <div className="w-1.5 h-1.5 bg-zinc-600 rounded-full animate-bounce" />
                <div className="w-1.5 h-1.5 bg-zinc-600 rounded-full animate-bounce [animation-delay:0.2s]" />
                <div className="w-1.5 h-1.5 bg-zinc-600 rounded-full animate-bounce [animation-delay:0.4s]" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area - Sleek Black Button Style */}
        <div className="p-4 bg-zinc-900/30 border-t border-zinc-800/50">
          <div className="flex items-center gap-2">
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type a message..."
              disabled={isLoading}
              className="flex-1 px-4 py-2.5 bg-black border border-zinc-800 rounded-xl text-sm text-zinc-200 placeholder-zinc-700 focus:outline-none focus:border-zinc-600 focus:ring-1 focus:ring-zinc-600 transition-all"
            />
            <button
              onClick={handleSend}
              disabled={!inputValue.trim() || isLoading}
              className="p-2.5 bg-black text-white rounded-xl border border-zinc-700 shadow-lg hover:bg-zinc-900 hover:border-zinc-500 transition-all active:scale-95 disabled:opacity-30 group"
            >
              <svg className="w-5 h-5 text-white group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Floating Action Button - Professional Look */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`fixed bottom-6 right-6 w-14 h-14 rounded-2xl shadow-2xl z-[999] flex items-center justify-center transition-all duration-500 hover:scale-110 active:scale-90 ${
          isOpen 
            ? "bg-zinc-800 text-white rotate-180" 
            : "bg-zinc-900 border border-zinc-800 text-white shadow-black/80"
        }`}
      >
        {isOpen ? (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        )}
      </button>
    </>
  );
}