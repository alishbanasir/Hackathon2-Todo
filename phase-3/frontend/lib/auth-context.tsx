"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";
import { useRouter } from "next/navigation";
import { apiClient } from "./api-client";

// Backend URL for authentication - use environment variable or default to localhost
const BACKEND_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
// Normalize: remove trailing slashes and any path suffix to get just the origin
const normalizeUrl = (url: string): string => {
  try {
    return new URL(url).origin;
  } catch {
    return url.replace(/\/+$/, '');
  }
};
const API_BASE_URL = `${normalizeUrl(BACKEND_BASE_URL)}/api/v1`;

interface AuthContextType {
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string) => void;
  loginWithCredentials: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_STORAGE_KEY = "auth_token";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Load token from localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem(TOKEN_STORAGE_KEY);
    if (storedToken) {
      setToken(storedToken);
    }
    setIsLoading(false);
  }, []);

  // Configure API client with token provider and unauthorized handler
  useEffect(() => {
    // Token provider (T086)
    apiClient.setTokenProvider(() => token);

    // Unauthorized handler (T087) - redirect to login
    apiClient.setOnUnauthorized(() => {
      setToken(null);
      localStorage.removeItem(TOKEN_STORAGE_KEY);
      router.push("/login");
    });
  }, [token, router]);

  const login = (newToken: string) => {
    // Trim whitespace and newlines to prevent ISO-8859-1 encoding errors
    const cleanToken = newToken.trim().replace(/[\r\n]/g, '');
    setToken(cleanToken);
    localStorage.setItem(TOKEN_STORAGE_KEY, cleanToken);
  };

  const loginWithCredentials = async (email: string, password: string) => {
    const loginUrl = `${API_BASE_URL}/auth/login`;
    console.log("Attempting login to:", loginUrl);

    let response: Response;
    try {
      response = await fetch(loginUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });
    } catch (error) {
      console.error("Login fetch error:", error);
      if (error instanceof TypeError && error.message === "Failed to fetch") {
        throw new Error("Cannot connect to authentication server. Is Phase 2 backend running on port 8000?");
      }
      throw error;
    }

    console.log("Login response status:", response.status);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.log("Login error data:", errorData);
      throw new Error(errorData.detail || "Invalid email or password");
    }

    const data = await response.json();
    const newToken = data.token;

    // Trim and store the token
    const cleanToken = newToken.trim().replace(/[\r\n]/g, '');
    setToken(cleanToken);
    localStorage.setItem(TOKEN_STORAGE_KEY, cleanToken);
  };

  const register = async (email: string, password: string) => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || "Registration failed");
    }

    const data = await response.json();
    const newToken = data.token;

    // Trim and store the token
    const cleanToken = newToken.trim().replace(/[\r\n]/g, '');
    setToken(cleanToken);
    localStorage.setItem(TOKEN_STORAGE_KEY, cleanToken);
  };

  const logout = () => {
    setToken(null);
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    router.push("/login");
  };

  const value: AuthContextType = {
    token,
    isAuthenticated: !!token,
    login,
    loginWithCredentials,
    register,
    logout,
    isLoading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
