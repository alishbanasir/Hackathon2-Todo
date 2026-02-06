"use client";

import { useEffect } from "react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log error to console in development
    console.error("Application error:", error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="max-w-md w-full text-center space-y-6">
        <div className="space-y-2">
          <h1 className="text-4xl font-bold text-foreground">
            Something went wrong
          </h1>
          <p className="text-foreground/60">
            {error.message || "An unexpected error occurred"}
          </p>
          {error.digest && (
            <p className="text-sm text-foreground/40">Error ID: {error.digest}</p>
          )}
        </div>

        <button
          onClick={reset}
          className="px-6 py-3 bg-foreground text-background rounded-lg font-medium hover:opacity-90 transition-opacity"
        >
          Try again
        </button>

        <a
          href="/"
          className="block text-sm text-foreground/60 hover:text-foreground underline"
        >
          Return to home
        </a>
      </div>
    </div>
  );
}
