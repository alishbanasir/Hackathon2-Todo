"use client";

import { useAuth } from "@/lib/auth-context";
import FloatingChat from "./FloatingChat";

/**
 * Wrapper component that only renders FloatingChat when user is authenticated.
 * This prevents the chat from appearing on the login page.
 */
export default function FloatingChatWrapper() {
  const { isAuthenticated, isLoading } = useAuth();

  // Don't render anything while checking auth or if not authenticated
  if (isLoading || !isAuthenticated) {
    return null;
  }

  return <FloatingChat />;
}
