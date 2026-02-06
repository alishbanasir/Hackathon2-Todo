"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

export function RegisterForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { register } = useAuth();

  const validateEmail = (email: string): boolean => {
    // RFC 5322 simplified email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Client-side validation
    if (!email.trim()) {
      setError("Email is required");
      return;
    }

    if (!validateEmail(email)) {
      setError("Please enter a valid email address");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    setLoading(true);

    try {
      await register(email, password);
      // Router navigation handled by auth context
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
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
          error={error && !email ? error : undefined}
        />

        <Input
          type="password"
          label="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Minimum 8 characters"
          disabled={loading}
          autoComplete="new-password"
          showPasswordToggle
          error={error && password.length > 0 && password.length < 8 ? error : undefined}
        />
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
        {loading ? "Creating account..." : "Create account"}
      </Button>

      <p className="text-center text-sm text-neutral-400 tracking-tight">
        Already have an account?{" "}
        <Link
          href="/login"
          className="text-white font-medium hover:text-neutral-300 transition-colors underline underline-offset-4"
        >
          Sign in
        </Link>
      </p>
    </form>
  );
}
