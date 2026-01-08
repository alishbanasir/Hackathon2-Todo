/**
 * TodoForm component for creating new todos.
 */

"use client";

import { useState } from "react";
import { apiClient } from "@/lib/api-client";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

interface TodoFormProps {
  onSuccess?: () => void;
}

export function TodoForm({ onSuccess }: TodoFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Client-side validation
    if (!title.trim()) {
      setError("Title is required");
      return;
    }

    if (title.length > 200) {
      setError("Title must be 200 characters or less");
      return;
    }

    if (description.length > 2000) {
      setError("Description must be 2000 characters or less");
      return;
    }

    setIsSubmitting(true);

    try {
      await apiClient.createTodo({
        title: title.trim(),
        description: description.trim(),
      });

      // Clear form on success
      setTitle("");
      setDescription("");
      setError("");

      // Notify parent component
      if (onSuccess) {
        onSuccess();
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to create todo. Please try again."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        type="text"
        label="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="What needs to be done?"
        disabled={isSubmitting}
        error={error && !title.trim() ? error : undefined}
        required
        maxLength={200}
      />

      <div>
        <label
          htmlFor="description"
          className="block text-sm font-medium text-neutral-200 tracking-tight mb-2"
        >
          Description (optional)
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Add more details..."
          disabled={isSubmitting}
          maxLength={2000}
          rows={3}
          className="w-full px-3.5 py-2.5 bg-neutral-950 border border-neutral-800 hover:border-neutral-700 rounded-md text-white text-sm placeholder:text-neutral-500 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-black focus:border-transparent disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-200"
        />
        <p className="mt-2 text-xs text-neutral-500 tracking-tight">
          {description.length}/2000 characters
        </p>
      </div>

      {error && title.trim() && (
        <p className="text-sm text-red-500 tracking-tight">{error}</p>
      )}

      <Button
        type="submit"
        variant="primary"
        disabled={isSubmitting || !title.trim()}
        className="w-full"
      >
        {isSubmitting ? "Creating..." : "Create Todo"}
      </Button>
    </form>
  );
}
