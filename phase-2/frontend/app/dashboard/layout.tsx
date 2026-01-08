"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { useAuth } from "@/lib/auth-context";
import { LogoutButton } from "@/components/auth/LogoutButton";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Redirect to login if not authenticated
    if (!loading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, loading, router]);

  // Show loading state while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <p className="text-neutral-500 tracking-tight">Loading...</p>
      </div>
    );
  }

  // Don't render dashboard if not authenticated
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-black">
      {/* Header */}
      <header className="border-b border-neutral-900 bg-black/95 backdrop-blur supports-[backdrop-filter]:bg-black/80 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-5 flex items-center justify-between">
          <div className="flex items-center">
            <Image
              src="/logo.png"
              alt="Todo App"
              width={160}
              height={40}
              className="h-10 w-auto"
              priority
            />
          </div>
          <LogoutButton />
        </div>
      </header>

      {/* Main content */}
      <main className="container mx-auto px-6 py-10">{children}</main>
    </div>
  );
}
