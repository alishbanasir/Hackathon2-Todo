"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

export function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Client-side validation
    if (!email.trim() || !password) {
      setError("Please enter both email and password");
      return;
    }

    setLoading(true);

    try {
      await login(email, password);
      // Router navigation handled by auth context
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 w-full">
      <div className="space-y-4">
        <Input
          type="email"
          label="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          disabled={loading}
          autoComplete="email"
        />

        <div>
          <Input
            type="password"
            label="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            disabled={loading}
            autoComplete="current-password"
            showPasswordToggle
          />
          <div className="mt-2 text-right">
            <Link
              href="/forgot-password"
              className="text-sm text-neutral-400 hover:text-white transition-colors tracking-tight"
            >
              Forgot password?
            </Link>
          </div>
        </div>
      </div>

      {error && (
        <div
          className="px-4 py-3 bg-red-950 border border-red-800 rounded-md text-red-400 text-sm tracking-tight"
          role="alert"
        >
          {error}
        </div>
      )}

      <Button
        type="submit"
        disabled={loading}
        className="w-full"
        size="lg"
      >
        {loading ? "Signing in..." : "Sign in"}
      </Button>

      <p className="text-center text-sm text-neutral-400 tracking-tight">
        Don't have an account?{" "}
        <Link
          href="/register"
          className="text-white font-medium hover:text-neutral-300 transition-colors underline underline-offset-4"
        >
          Create one
        </Link>
      </p>
    </form>
  );
}
