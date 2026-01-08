"use client";

import { useAuth } from "@/lib/auth-context";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { TodoForm } from "@/components/todos/TodoForm";
import { TodoList } from "@/components/todos/TodoList";
import { apiClient } from "@/lib/api-client";
import { useState, useEffect } from "react";
import { Todo } from "@/lib/types";

export default function DashboardPage() {
  const { user } = useAuth();
  const [todos, setTodos] = useState<Todo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchTodos = async () => {
    setIsLoading(true);
    setError("");

    try {
      const response = await apiClient.getTodos();
      setTodos(response.todos);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load todos. Please try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTodos();
  }, []);

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="space-y-3">
        <h2 className="text-3xl font-bold text-white tracking-tight">Dashboard</h2>
        <p className="text-neutral-400 tracking-tight">
          Welcome back, {user?.email || "user"}!
        </p>
      </div>

      {/* Create Todo Card */}
      <Card>
        <CardHeader>
          <CardTitle>Create New Todo</CardTitle>
          <CardDescription>
            Add a new task to your list
          </CardDescription>
        </CardHeader>
        <CardContent>
          <TodoForm onSuccess={fetchTodos} />
        </CardContent>
      </Card>

      {/* Todos List Card */}
      <Card>
        <CardHeader>
          <CardTitle>Your Todos</CardTitle>
          <CardDescription>
            Manage your tasks and stay organized
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-16">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-white border-r-transparent" role="status">
                <span className="sr-only">Loading...</span>
              </div>
              <p className="mt-4 text-sm text-neutral-500 tracking-tight">Loading todos...</p>
            </div>
          ) : error ? (
            <div className="text-center py-16">
              <p className="text-red-500 mb-4 tracking-tight">{error}</p>
              <button
                onClick={fetchTodos}
                className="text-sm text-white hover:text-neutral-300 underline underline-offset-4 transition-colors tracking-tight"
              >
                Try again
              </button>
            </div>
          ) : (
            <TodoList todos={todos} onUpdate={fetchTodos} />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
