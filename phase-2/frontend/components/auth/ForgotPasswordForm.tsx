"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api-client";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

export function ForgotPasswordForm() {
  const [step, setStep] = useState<"email" | "reset">("email");
  const [email, setEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    // Client-side validation
    if (!email.trim()) {
      setError("Please enter your email address");
      return;
    }

    setLoading(true);

    try {
      const response = await apiClient.forgotPassword(email);
      setSuccess(response.message);
      // Move to reset step
      setStep("reset");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to verify email");
    } finally {
      setLoading(false);
    }
  };

  const handleResetSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    // Client-side validation
    if (!newPassword || !confirmPassword) {
      setError("Please enter and confirm your new password");
      return;
    }

    if (newPassword.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);

    try {
      const response = await apiClient.resetPassword(email, newPassword);
      setSuccess(response.message);
      // Redirect to login after 2 seconds
      setTimeout(() => {
        router.push("/login");
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reset password");
    } finally {
      setLoading(false);
    }
  };

  if (step === "email") {
    return (
      <form onSubmit={handleEmailSubmit} className="space-y-6 w-full">
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
        </div>

        {error && (
          <div
            className="px-4 py-3 bg-red-950 border border-red-800 rounded-md text-red-400 text-sm tracking-tight"
            role="alert"
          >
            {error}
          </div>
        )}

        {success && (
          <div
            className="px-4 py-3 bg-green-950 border border-green-800 rounded-md text-green-400 text-sm tracking-tight"
            role="alert"
          >
            {success}
          </div>
        )}

        <Button
          type="submit"
          disabled={loading}
          className="w-full"
          size="lg"
        >
          {loading ? "Verifying..." : "Continue"}
        </Button>

        <p className="text-center text-sm text-neutral-400 tracking-tight">
          Remember your password?{" "}
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

  return (
    <form onSubmit={handleResetSubmit} className="space-y-6 w-full">
      <div className="space-y-4">
        <div className="px-4 py-3 bg-neutral-900 border border-neutral-800 rounded-md">
          <p className="text-sm text-neutral-300 tracking-tight">
            Resetting password for: <span className="font-medium text-white">{email}</span>
          </p>
        </div>

        <Input
          type="password"
          label="New Password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          placeholder="Minimum 8 characters"
          disabled={loading}
          autoComplete="new-password"
          showPasswordToggle
        />

        <Input
          type="password"
          label="Confirm Password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          placeholder="Re-enter your new password"
          disabled={loading}
          autoComplete="new-password"
          showPasswordToggle
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

      {success && (
        <div
          className="px-4 py-3 bg-green-950 border border-green-800 rounded-md text-green-400 text-sm tracking-tight"
          role="alert"
        >
          {success}
          <p className="mt-1 text-xs">Redirecting to login...</p>
        </div>
      )}

      <div className="flex gap-3">
        <Button
          type="button"
          variant="secondary"
          onClick={() => setStep("email")}
          disabled={loading}
          className="flex-1"
        >
          Back
        </Button>
        <Button
          type="submit"
          disabled={loading}
          className="flex-1"
          size="lg"
        >
          {loading ? "Resetting..." : "Reset Password"}
        </Button>
      </div>
    </form>
  );
}
