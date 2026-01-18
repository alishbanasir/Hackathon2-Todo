"use client";

export interface Todo {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
}

interface TodoDisplayProps {
  todos: Todo[];
  compact?: boolean;
}

export default function TodoDisplay({ todos, compact = false }: TodoDisplayProps) {
  if (todos.length === 0) {
    return (
      <div className="text-sm text-gray-500 italic">No todos to display</div>
    );
  }

  if (compact) {
    return (
      <div className="space-y-1">
        {todos.map((todo) => (
          <TodoItemCompact key={todo.id} todo={todo} />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {todos.map((todo) => (
        <TodoItem key={todo.id} todo={todo} />
      ))}
    </div>
  );
}

function TodoItem({ todo }: { todo: Todo }) {
  return (
    <div
      className={`border rounded-lg p-3 ${
        todo.completed
          ? "bg-gray-50 border-gray-200"
          : "bg-white border-blue-200"
      }`}
    >
      <div className="flex items-start space-x-3">
        {/* Checkbox */}
        <div className="flex-shrink-0 pt-0.5">
          {todo.completed ? (
            <svg
              className="h-5 w-5 text-green-500"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
          ) : (
            <svg
              className="h-5 w-5 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <circle cx="12" cy="12" r="10" strokeWidth={2} />
            </svg>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <h4
            className={`text-sm font-medium ${
              todo.completed
                ? "text-gray-500 line-through"
                : "text-gray-900"
            }`}
          >
            {todo.title}
          </h4>
          {todo.description && (
            <p
              className={`text-sm mt-1 ${
                todo.completed ? "text-gray-400" : "text-gray-600"
              }`}
            >
              {todo.description}
            </p>
          )}
          <div className="flex items-center mt-2 text-xs text-gray-500">
            <span>ID: {todo.id}</span>
            {todo.completed && (
              <>
                <span className="mx-2">•</span>
                <span className="text-green-600 font-medium">Completed</span>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function TodoItemCompact({ todo }: { todo: Todo }) {
  return (
    <div className="flex items-center space-x-2 text-sm">
      {/* Checkbox */}
      {todo.completed ? (
        <svg
          className="h-4 w-4 text-green-500 flex-shrink-0"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fillRule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
            clipRule="evenodd"
          />
        </svg>
      ) : (
        <svg
          className="h-4 w-4 text-gray-400 flex-shrink-0"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <circle cx="12" cy="12" r="10" strokeWidth={2} />
        </svg>
      )}

      {/* Text */}
      <span
        className={`flex-1 truncate ${
          todo.completed
            ? "text-gray-500 line-through"
            : "text-gray-900"
        }`}
      >
        {todo.title}
      </span>

      {/* ID Badge */}
      <span className="text-xs text-gray-500 flex-shrink-0">#{todo.id}</span>
    </div>
  );
}
