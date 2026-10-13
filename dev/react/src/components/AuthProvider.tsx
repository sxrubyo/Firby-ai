"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const router = useRouter();

  useEffect(() => {
    const key = localStorage.getItem("dev_master_key");
    if (!key) {
      router.replace("/dev-portal/login/");
    } else {
      setIsAuthenticated(true);
    }
  }, [router]);

  if (!isAuthenticated) {
    return <div className="min-h-screen bg-black flex items-center justify-center px-4"><p className="text-white text-sm">Verificando seguridad...</p></div>;
  }

  return <>{children}</>;
}
