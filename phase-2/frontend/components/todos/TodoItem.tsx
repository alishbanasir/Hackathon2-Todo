/**
 * TodoItem component for displaying a single todo with actions.
 */

"use client";

import { useState } from "react";
import { Todo } from "@/lib/types";
import { apiClient } from "@/lib/api-client";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

interface TodoItemProps {
  todo: Todo;
  onUpdate?: () => void;
}

export function TodoItem({ todo, onUpdate }: TodoItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(todo.title);
  const [editDescription, setEditDescription] = useState(todo.description);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleToggle = async () => {
    setIsLoading(true);
    setError("");

    try {
      await apiClient.toggleTodo(todo.id);
      if (onUpdate) {
        onUpdate();
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to toggle todo"
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdate = async () => {
    setIsLoading(true);
    setError("");

    // Validation
    if (!editTitle.trim()) {
      setError("Title is required");
      setIsLoading(false);
      return;
    }

    if (editTitle.length > 200) {
      setError("Title must be 200 characters or less");
      setIsLoading(false);
      return;
    }

    if (editDescription.length > 2000) {
      setError("Description must be 2000 characters or less");
      setIsLoading(false);
      return;
    }

    try {
      await apiClient.updateTodo(todo.id, {
        title: editTitle.trim(),
        description: editDescription.trim(),
      });
      setIsEditing(false);
      if (onUpdate) {
        onUpdate();
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to update todo"
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this todo?")) {
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      await apiClient.deleteTodo(todo.id);
      if (onUpdate) {
        onUpdate();
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to delete todo"
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditTitle(todo.title);
    setEditDescription(todo.description);
    setError("");
  };

  if (isEditing) {
    return (
      <div className="border border-neutral-700 rounded-lg p-5 bg-neutral-900 shadow-lg">
        <div className="space-y-4">
          <Input
            type="text"
            label="Title"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            disabled={isLoading}
            error={error && !editTitle.trim() ? error : undefined}
            required
            maxLength={200}
          />

          <div>
            <label
              htmlFor={`edit-description-${todo.id}`}
              className="block text-sm font-medium text-neutral-200 tracking-tight mb-2"
            >
              Description (optional)
            </label>
            <textarea
              id={`edit-description-${todo.id}`}
              value={editDescription}
              onChange={(e) => setEditDescription(e.target.value)}
              disabled={isLoading}
              maxLength={2000}
              rows={3}
              className="w-full px-3.5 py-2.5 bg-neutral-950 border border-neutral-800 hover:border-neutral-700 rounded-md text-white text-sm placeholder:text-neutral-500 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-black focus:border-transparent disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-200"
            />
          </div>

          {error && editTitle.trim() && (
            <p className="text-sm text-red-500 tracking-tight">{error}</p>
          )}

          <div className="flex gap-2">
            <Button
              onClick={handleUpdate}
              variant="primary"
              size="sm"
              disabled={isLoading || !editTitle.trim()}
            >
              {isLoading ? "Saving..." : "Save"}
            </Button>
            <Button
              onClick={handleCancelEdit}
              variant="secondary"
              size="sm"
              disabled={isLoading}
            >
              Cancel
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="border border-neutral-800 rounded-lg p-4 bg-neutral-950 hover:border-neutral-700 transition-all duration-200">
      <div className="flex items-start gap-4">
        {/* Checkbox */}
        <input
          type="checkbox"
          checked={todo.completed}
          onChange={handleToggle}
          disabled={isLoading}
          className="mt-1 h-5 w-5 rounded border-neutral-700 bg-neutral-900 text-white focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-black disabled:cursor-not-allowed disabled:opacity-40 transition-all duration-200 cursor-pointer"
          aria-label={`Mark "${todo.title}" as ${todo.completed ? "incomplete" : "complete"}`}
        />

        {/* Content */}
        <div className="flex-1 min-w-0">
          <h3
            className={`text-base font-medium break-words tracking-tight ${
              todo.completed
                ? "line-through text-neutral-500"
                : "text-white"
            }`}
          >
            {todo.title}
          </h3>

          {todo.description && (
            <p
              className={`mt-2 text-sm break-words tracking-tight ${
                todo.completed ? "text-neutral-600" : "text-neutral-400"
              }`}
            >
              {todo.description}
            </p>
          )}

          <p className="mt-3 text-xs text-neutral-600 tracking-tight">
            Created: {new Date(todo.created_at).toLocaleString("en-US", {
              year: "numeric",
              month: "short",
              day: "numeric",
              hour: "2-digit",
              minute: "2-digit",
            })}
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <Button
            onClick={() => setIsEditing(true)}
            variant="secondary"
            size="sm"
            disabled={isLoading}
          >
            Edit
          </Button>
          <Button
            onClick={handleDelete}
            variant="danger"
            size="sm"
            disabled={isLoading}
          >
            Delete
          </Button>
        </div>
      </div>

      {error && (
        <p className="mt-3 text-sm text-red-500 tracking-tight">{error}</p>
      )}
    </div>
  );
}
