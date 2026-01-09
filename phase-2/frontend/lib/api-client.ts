/**
 * API client for backend communication with authentication support.
 */

import {
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  Todo,
  TodoCreateRequest,
  TodoListResponse,
  TodoUpdateRequest,
} from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

/**
 * Custom error class for API errors.
 */
export class TodoApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: unknown
  ) {
    super(message);
    this.name = "TodoApiError";
  }
}

/**
 * API client for making authenticated requests to the backend.
 */
export class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl;
    // Load token from localStorage if available (client-side only)
    if (typeof window !== "undefined") {
      this.token = localStorage.getItem("auth_token");
    }
  }

  /**
   * Set the authentication token.
   */
  setToken(token: string): void {
    this.token = token;
    if (typeof window !== "undefined") {
      localStorage.setItem("auth_token", token);
    }
  }

  /**
   * Remove the authentication token.
   */
  clearToken(): void {
    this.token = null;
    if (typeof window !== "undefined") {
      localStorage.removeItem("auth_token");
    }
  }

  /**
   * Get the current authentication token.
   */
  getToken(): string | null {
    return this.token;
  }

  /**
   * Make an authenticated HTTP request.
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    // Add Authorization header if token exists
    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      // Handle non-200 responses
      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        let errorDetails: unknown;

        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
          errorDetails = errorData;
        } catch {
          // Response is not JSON, use status text
        }

        throw new TodoApiError(errorMessage, response.status, errorDetails);
      }

      // Parse JSON response
      const data = await response.json();
      return data as T;
    } catch (error) {
      if (error instanceof TodoApiError) {
        throw error;
      }

      // Network or other errors
      throw new TodoApiError(
        error instanceof Error ? error.message : "Network error occurred"
      );
    }
  }

  /**
   * Register a new user.
   */
  async register(email: string, password: string): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password } as RegisterRequest),
    });

    // Automatically set token after successful registration
    this.setToken(response.token);

    return response;
  }

  /**
   * Login with email and password.
   */
  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password } as LoginRequest),
    });

    // Automatically set token after successful login
    this.setToken(response.token);

    return response;
  }

  /**
   * Logout (client-side token removal).
   */
  async logout(): Promise<void> {
    try {
      // Call logout endpoint (optional, for consistency)
      await this.request("/auth/logout", {
        method: "POST",
      });
    } finally {
      // Always clear token, even if API call fails
      this.clearToken();
    }
  }

  /**
   * Get all todos for the authenticated user.
   */
  async getTodos(): Promise<TodoListResponse> {
    return this.request<TodoListResponse>("/todos");
  }

  /**
   * Get a specific todo by ID.
   */
  async getTodoById(id: number): Promise<Todo> {
    return this.request<Todo>(`/todos/${id}`);
  }

  /**
   * Create a new todo.
   */
  async createTodo(request: TodoCreateRequest): Promise<Todo> {
    return this.request<Todo>("/todos", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  /**
   * Update an existing todo.
   */
  async updateTodo(id: number, request: TodoUpdateRequest): Promise<Todo> {
    return this.request<Todo>(`/todos/${id}`, {
      method: "PUT",
      body: JSON.stringify(request),
    });
  }

  /**
   * Toggle todo completion status.
   */
  async toggleTodo(id: number): Promise<Todo> {
    return this.request<Todo>(`/todos/${id}/toggle`, {
      method: "PATCH",
    });
  }

  /**
   * Delete a todo.
   */
  async deleteTodo(id: number): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/todos/${id}`, {
      method: "DELETE",
    });
  }

  /**
   * Check if email exists for password reset.
   */
  async forgotPassword(email: string): Promise<{ message: string }> {
    return this.request<{ message: string }>("/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email }),
    });
  }

  /**
   * Reset password with email and new password.
   */
  async resetPassword(email: string, new_password: string): Promise<{ message: string }> {
    return this.request<{ message: string }>("/auth/reset-password", {
      method: "POST",
      body: JSON.stringify({ email, new_password }),
    });
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
