"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiClient, TodoApiError } from "@/lib/api-client";
import { User } from "@/lib/types";

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  // Load token from localStorage on mount
  useEffect(() => {
    const storedToken = apiClient.getToken();
    if (storedToken) {
      setToken(storedToken);
      // TODO: Optionally verify token and load user data from backend
      // For now, we'll just check if token exists
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await apiClient.login(email, password);
      setToken(response.token);
      setUser(response.user);
      router.push("/dashboard");
    } catch (error) {
      if (error instanceof TodoApiError) {
        throw new Error(error.message);
      }
      throw new Error("Login failed. Please try again.");
    }
  };

  const register = async (email: string, password: string) => {
    try {
      const response = await apiClient.register(email, password);
      setToken(response.token);
      setUser(response.user);
      router.push("/dashboard");
    } catch (error) {
      if (error instanceof TodoApiError) {
        throw new Error(error.message);
      }
      throw new Error("Registration failed. Please try again.");
    }
  };

  const logout = async () => {
    await apiClient.logout();
    setToken(null);
    setUser(null);
    router.push("/login");
  };

  const value: AuthContextType = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!token,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
