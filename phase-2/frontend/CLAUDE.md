# Claude Code Context: Phase II Frontend (Next.js)

This file provides context for AI agents working in `phase-2/frontend/` directory.

## Purpose

Next.js 16+ TypeScript frontend providing responsive web interface for multi-user todo management with Better Auth JWT authentication.

## Technology Stack

- **Framework**: Next.js 16+ (App Router with React Server Components)
- **Language**: TypeScript 5.x (strict mode)
- **Styling**: Tailwind CSS 3.x (mobile-first responsive design)
- **Auth**: Better Auth (JWT token management)
- **State Management**: React Server Components + minimal client state
- **Testing**: Vitest, React Testing Library
- **Linting**: ESLint (Next.js config), Prettier

## Directory Structure

```
frontend/
├── app/                        # Next.js App Router
│   ├── (auth)/                # Auth route group (public)
│   │   ├── login/
│   │   │   └── page.tsx      # Login page
│   │   └── register/
│   │       └── page.tsx      # Registration page
│   │
│   ├── (dashboard)/           # Protected route group
│   │   ├── layout.tsx        # Dashboard layout with auth check
│   │   ├── page.tsx          # Todo list page
│   │   └── todos/
│   │       └── [id]/
│   │           └── page.tsx  # Todo detail page
│   │
│   ├── layout.tsx            # Root layout (providers, fonts)
│   ├── globals.css           # Tailwind CSS imports
│   └── error.tsx             # Global error boundary
│
├── components/                # Reusable React components
│   ├── ui/                   # Base UI components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   └── Modal.tsx
│   │
│   ├── auth/                 # Auth-related components
│   │   ├── LoginForm.tsx
│   │   ├── RegisterForm.tsx
│   │   └── LogoutButton.tsx
│   │
│   └── todos/                # Todo-related components
│       ├── TodoList.tsx
│       ├── TodoItem.tsx
│       ├── TodoForm.tsx
│       └── TodoDeleteConfirm.tsx
│
├── lib/                      # Utility functions and services
│   ├── api-client.ts        # API client (fetch wrapper)
│   ├── auth-context.tsx     # Auth state context provider
│   ├── types.ts             # TypeScript type definitions
│   └── utils.ts             # Utility functions (classnames, etc.)
│
├── hooks/                    # Custom React hooks
│   ├── useAuth.ts           # Auth hook (from context)
│   └── useTodos.ts          # Todos data fetching hook
│
├── public/                   # Static assets
│   ├── favicon.ico
│   └── images/
│
├── __tests__/                # Vitest tests
│   ├── components/
│   └── lib/
│
├── .env.local.example        # Example environment variables
├── .env.local                # Actual environment variables (gitignored)
├── package.json              # Dependencies and scripts
├── tsconfig.json             # TypeScript configuration
├── tailwind.config.ts        # Tailwind CSS configuration
├── next.config.js            # Next.js configuration
├── vitest.config.ts          # Vitest configuration
└── .eslintrc.json            # ESLint configuration
```

## Critical Requirements

### 1. Authentication Flow

**JWT Token Management**:

```typescript
// lib/auth-context.tsx
'use client';

import { createContext, useContext, useState, useEffect } from 'react';

interface AuthState {
  token: string | null;
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.Node }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Load token from localStorage on mount
    const storedToken = localStorage.getItem('auth_token');
    if (storedToken) {
      setToken(storedToken);
      // Optionally fetch user profile
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) throw new Error('Login failed');

    const data = await response.json();
    setToken(data.token);
    setUser(data.user);
    localStorage.setItem('auth_token', data.token);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('auth_token');
  };

  return (
    <AuthContext.Provider value={{ token, user, login, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

**Protected Routes**:

```typescript
// app/(dashboard)/layout.tsx
'use client';

import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function DashboardLayout({ children }: { children: React.Node }) {
  const { token, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !token) {
      router.push('/login');
    }
  }, [token, isLoading, router]);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!token) {
    return null; // Will redirect in useEffect
  }

  return <div>{children}</div>;
}
```

### 2. API Client (Type-Safe Fetch Wrapper)

```typescript
// lib/api-client.ts
import { Todo, TodoCreateRequest, TodoUpdateRequest } from './types';

class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL!;
  }

  private getAuthToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('auth_token');
  }

  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const token = this.getAuthToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options?.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new ApiError(response.status, error.error || 'Request failed');
    }

    return response.json();
  }

  // Auth endpoints
  async register(email: string, password: string) {
    return this.request<{ token: string; user: User }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async login(email: string, password: string) {
    return this.request<{ token: string; user: User }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  // Todo endpoints
  async getTodos(): Promise<{ todos: Todo[]; count: number }> {
    return this.request('/todos');
  }

  async getTodoById(id: number): Promise<Todo> {
    return this.request(`/todos/${id}`);
  }

  async createTodo(data: TodoCreateRequest): Promise<Todo> {
    return this.request('/todos', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateTodo(id: number, data: TodoUpdateRequest): Promise<Todo> {
    return this.request(`/todos/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async toggleTodo(id: number): Promise<Todo> {
    return this.request(`/todos/${id}/toggle`, {
      method: 'PATCH',
    });
  }

  async deleteTodo(id: number): Promise<void> {
    await this.request(`/todos/${id}`, {
      method: 'DELETE',
    });
  }
}

export const apiClient = new ApiClient();

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}
```

### 3. Server Components vs Client Components

**Use Server Components by default** (better performance):

```typescript
// app/(dashboard)/page.tsx - Server Component (default)
import { TodoList } from '@/components/todos/TodoList';
import { apiClient } from '@/lib/api-client';

export default async function DashboardPage() {
  // Direct server-side data fetching
  const { todos } = await apiClient.getTodos();

  return (
    <div>
      <h1>My Todos</h1>
      <TodoList todos={todos} />
    </div>
  );
}
```

**Use Client Components only for interactivity**:

```typescript
// components/todos/TodoForm.tsx - Client Component
'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api-client';
import { useRouter } from 'next/navigation';

export function TodoForm() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      await apiClient.createTodo({ title, description });
      router.refresh(); // Refresh server component data
      setTitle('');
      setDescription('');
    } catch (error) {
      console.error('Failed to create todo:', error);
      alert('Failed to create todo');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Todo title"
        required
        maxLength={200}
      />
      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Description (optional)"
        maxLength={2000}
      />
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Creating...' : 'Create Todo'}
      </button>
    </form>
  );
}
```

### 4. Tailwind CSS (Mobile-First Responsive Design)

**Use mobile-first breakpoints**:

```typescript
// components/todos/TodoItem.tsx
export function TodoItem({ todo }: { todo: Todo }) {
  return (
    <div className="
      w-full
      p-4
      border
      rounded

      md:p-6           /* Tablet: larger padding */
      md:flex          /* Tablet: flex layout */
      md:items-center  /* Tablet: center items */

      lg:p-8          /* Desktop: even larger padding */
    ">
      <h3 className="
        text-base
        font-medium

        md:text-lg     /* Tablet: larger text */
        lg:text-xl     /* Desktop: even larger text */
      ">
        {todo.title}
      </h3>
    </div>
  );
}
```

**Responsive grid layouts**:

```typescript
<div className="
  grid
  grid-cols-1       /* Mobile: 1 column */
  gap-4

  md:grid-cols-2    /* Tablet: 2 columns */
  lg:grid-cols-3    /* Desktop: 3 columns */
  xl:grid-cols-4    /* Large desktop: 4 columns */
">
  {todos.map(todo => <TodoItem key={todo.id} todo={todo} />)}
</div>
```

## TypeScript Patterns

### Type Definitions

```typescript
// lib/types.ts
export interface User {
  id: string;  // UUID
  email: string;
  created_at: string;  // ISO 8601 datetime
}

export interface Todo {
  id: number;
  user_id: string;  // UUID
  title: string;
  description: string;
  completed: boolean;
  created_at: string;  // ISO 8601 datetime
}

export interface TodoCreateRequest {
  title: string;
  description?: string;
}

export interface TodoUpdateRequest {
  title?: string;
  description?: string;
}

export interface ApiErrorResponse {
  error: string;
  details?: string;
}
```

### Strict TypeScript Mode

**tsconfig.json**:
```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true
  }
}
```

**No `any` types**:

```typescript
// ❌ WRONG
function processTodo(todo: any) {  // Type safety violation!
  return todo.title;
}

// ✅ CORRECT
function processTodo(todo: Todo): string {
  return todo.title;
}
```

## Form Validation

**Client-side validation**:

```typescript
// components/auth/RegisterForm.tsx
'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/auth-context';

export function RegisterForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});
  const { register } = useAuth();

  const validate = () => {
    const newErrors: typeof errors = {};

    // Email validation
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(email)) {
      newErrors.email = 'Invalid email address format';
    }

    // Password validation
    if (password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    try {
      await register(email, password);
      // Redirect handled by auth context
    } catch (error) {
      setErrors({ email: 'Registration failed. Email may already be in use.' });
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          required
        />
        {errors.email && <p className="text-red-500 text-sm">{errors.email}</p>}
      </div>

      <div>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          required
          minLength={8}
        />
        {errors.password && <p className="text-red-500 text-sm">{errors.password}</p>}
      </div>

      <button type="submit">Register</button>
    </form>
  );
}
```

## Error Handling

### Error Boundaries

```typescript
// app/error.tsx - Global error boundary
'use client';

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log error to monitoring service
    console.error('Application error:', error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h2 className="text-2xl font-bold mb-4">Something went wrong!</h2>
      <p className="text-gray-600 mb-6">
        We're sorry for the inconvenience. Please try again.
      </p>
      <button
        onClick={reset}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Try again
      </button>
    </div>
  );
}
```

### Network Error Handling

```typescript
// lib/api-client.ts
private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  try {
    const response = await fetch(`${this.baseUrl}${endpoint}`, options);

    if (!response.ok) {
      const error = await response.json();
      throw new ApiError(response.status, error.error || 'Request failed');
    }

    return response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;

    // Network error (no response)
    throw new ApiError(0, 'Network error. Please check your connection and try again.');
  }
}
```

## Environment Variables

**Required variables** (`.env.local`):
```env
BETTER_AUTH_SECRET=<same-secret-as-backend>
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

**Access in code**:

```typescript
// Client-side (prefixed with NEXT_PUBLIC_)
const apiUrl = process.env.NEXT_PUBLIC_API_URL;

// Server-side (any variable)
const authSecret = process.env.BETTER_AUTH_SECRET;
```

## Testing

### Component Tests

```typescript
// __tests__/components/TodoForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { TodoForm } from '@/components/todos/TodoForm';
import { apiClient } from '@/lib/api-client';

vi.mock('@/lib/api-client');

describe('TodoForm', () => {
  it('validates required title', async () => {
    render(<TodoForm />);

    const submitButton = screen.getByRole('button', { name: /create/i });
    fireEvent.click(submitButton);

    expect(await screen.findByText(/title is required/i)).toBeInTheDocument();
  });

  it('creates todo successfully', async () => {
    const mockCreateTodo = vi.fn().mockResolvedValue({ id: 1, title: 'Test todo' });
    (apiClient.createTodo as jest.Mock) = mockCreateTodo;

    render(<TodoForm />);

    const titleInput = screen.getByPlaceholderText(/todo title/i);
    fireEvent.change(titleInput, { target: { value: 'Test todo' } });

    const submitButton = screen.getByRole('button', { name: /create/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockCreateTodo).toHaveBeenCalledWith({ title: 'Test todo', description: '' });
    });
  });
});
```

## Common Mistakes to Avoid

### ❌ Don't Use Client Components Unnecessarily

```typescript
// ❌ WRONG - Unnecessary "use client"
'use client';

export default function StaticPage() {
  return <div>Static content</div>;  // No interactivity!
}

// ✅ CORRECT - Server Component (default)
export default function StaticPage() {
  return <div>Static content</div>;
}
```

### ❌ Don't Store Sensitive Data in Client State

```typescript
// ❌ WRONG - Exposing user password
const [password, setPassword] = useState('');
// Password visible in React DevTools!

// ✅ CORRECT - Clear password after submission
const handleLogin = async () => {
  await login(email, password);
  setPassword('');  // Clear immediately after use
};
```

### ❌ Don't Ignore TypeScript Errors

```typescript
// ❌ WRONG - Using @ts-ignore
// @ts-ignore
const title = todo.titel;  // Typo not caught!

// ✅ CORRECT - Fix the error
const title = todo.title;  // TypeScript catches typos
```

## Quick Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Type checking
npm run type-check

# Linting
npm run lint

# Format code
npm run format
```

## References

- Parent context: `phase-2/CLAUDE.md`
- Specification: `phase-2/specs/spec.md`
- API contract: `phase-2/specs/contracts/openapi.yaml`
- Next.js docs: https://nextjs.org/docs
- Tailwind docs: https://tailwindcss.com/docs
- TypeScript docs: https://www.typescriptlang.org/docs
