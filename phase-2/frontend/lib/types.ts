/**
 * TypeScript type definitions for the Todo application.
 * These types match the backend API contracts defined in openapi.yaml.
 */

/**
 * User entity representing an authenticated user.
 */
export interface User {
  id: string; // UUID
  email: string;
  created_at: string; // ISO 8601 datetime
}

/**
 * Todo entity representing a single task item.
 */
export interface Todo {
  id: number;
  user_id: string; // UUID
  title: string;
  description: string;
  completed: boolean;
  created_at: string; // ISO 8601 datetime
}

/**
 * Request payload for user registration.
 */
export interface RegisterRequest {
  email: string;
  password: string;
}

/**
 * Request payload for user login.
 */
export interface LoginRequest {
  email: string;
  password: string;
}

/**
 * Response from authentication endpoints (register/login).
 */
export interface AuthResponse {
  token: string; // JWT token
  user: User;
}

/**
 * Request payload for creating a new todo.
 */
export interface TodoCreateRequest {
  title: string; // 1-200 characters
  description?: string; // 0-2000 characters (optional)
}

/**
 * Request payload for updating an existing todo.
 */
export interface TodoUpdateRequest {
  title?: string; // 1-200 characters (optional)
  description?: string; // 0-2000 characters (optional)
}

/**
 * Generic error response from API.
 */
export interface ApiError {
  detail: string;
  status_code?: number;
}

/**
 * Generic list response wrapper.
 */
export interface ListResponse<T> {
  items: T[];
  total: number;
}

/**
 * Response from GET /todos endpoint.
 */
export interface TodoListResponse {
  todos: Todo[];
  total: number;
}
