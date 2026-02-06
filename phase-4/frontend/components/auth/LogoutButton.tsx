"use client";

import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/Button";

export function LogoutButton() {
  const { logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <Button variant="ghost" onClick={handleLogout}>
      Logout
    </Button>
  );
}
