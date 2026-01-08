/**
 * TodoList component for displaying a list of todos with filtering.
 */

"use client";

import { useState } from "react";
import { Todo } from "@/lib/types";
import { TodoItem } from "./TodoItem";

interface TodoListProps {
  todos: Todo[];
  onUpdate?: () => void;
}

type FilterType = "all" | "active" | "completed";

export function TodoList({ todos, onUpdate }: TodoListProps) {
  const [filter, setFilter] = useState<FilterType>("all");

  // Filter todos based on selected filter
  const filteredTodos = todos.filter((todo) => {
    if (filter === "active") return !todo.completed;
    if (filter === "completed") return todo.completed;
    return true; // "all"
  });

  // Calculate counts
  const totalCount = todos.length;
  const activeCount = todos.filter((t) => !t.completed).length;
  const completedCount = todos.filter((t) => t.completed).length;

  if (totalCount === 0) {
    return (
      <div className="text-center py-16">
        <svg
          className="mx-auto h-12 w-12 text-neutral-700"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
          />
        </svg>
        <h3 className="mt-4 text-sm font-medium text-white tracking-tight">No todos yet</h3>
        <p className="mt-2 text-sm text-neutral-500 tracking-tight">
          Get started by creating a new todo above.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filter Tabs */}
      <div className="border-b border-neutral-800">
        <nav className="-mb-px flex space-x-8" aria-label="Tabs">
          <button
            onClick={() => setFilter("all")}
            className={`
              whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm tracking-tight transition-all duration-200
              ${
                filter === "all"
                  ? "border-white text-white"
                  : "border-transparent text-neutral-500 hover:text-neutral-300 hover:border-neutral-700"
              }
            `}
          >
            All
            <span className={`ml-2.5 py-0.5 px-2 rounded-full text-xs font-medium tracking-tight ${
              filter === "all"
                ? "bg-white text-black"
                : "bg-neutral-900 text-neutral-400"
            }`}>
              {totalCount}
            </span>
          </button>

          <button
            onClick={() => setFilter("active")}
            className={`
              whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm tracking-tight transition-all duration-200
              ${
                filter === "active"
                  ? "border-white text-white"
                  : "border-transparent text-neutral-500 hover:text-neutral-300 hover:border-neutral-700"
              }
            `}
          >
            Active
            <span className={`ml-2.5 py-0.5 px-2 rounded-full text-xs font-medium tracking-tight ${
              filter === "active"
                ? "bg-white text-black"
                : "bg-neutral-900 text-neutral-400"
            }`}>
              {activeCount}
            </span>
          </button>

          <button
            onClick={() => setFilter("completed")}
            className={`
              whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm tracking-tight transition-all duration-200
              ${
                filter === "completed"
                  ? "border-white text-white"
                  : "border-transparent text-neutral-500 hover:text-neutral-300 hover:border-neutral-700"
              }
            `}
          >
            Completed
            <span className={`ml-2.5 py-0.5 px-2 rounded-full text-xs font-medium tracking-tight ${
              filter === "completed"
                ? "bg-white text-black"
                : "bg-neutral-900 text-neutral-400"
            }`}>
              {completedCount}
            </span>
          </button>
        </nav>
      </div>

      {/* Todos List */}
      {filteredTodos.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-sm text-neutral-500 tracking-tight">
            No {filter} todos found.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredTodos.map((todo) => (
            <TodoItem key={todo.id} todo={todo} onUpdate={onUpdate} />
          ))}
        </div>
      )}
    </div>
  );
}
