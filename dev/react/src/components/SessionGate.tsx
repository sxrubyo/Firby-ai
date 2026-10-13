"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

type SessionGateProps = {
  children: React.ReactNode;
  allowedKeys: string[];
  redirectTo: string;
  loadingLabel?: string; // Kept for backwards compatibility but not used
};

export function SessionGate({
  children,
  allowedKeys,
  redirectTo,
}: SessionGateProps) {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const userEmail = typeof window !== "undefined" ? localStorage.getItem("firby_user_email") : null;
    const isOnboarded = typeof window !== "undefined" ? localStorage.getItem("firby_onboarding_done") === "true" : false;

    // Strict check: If an account is logged in and onboarding is not done, redirect to /onboarding
    if (userEmail && userEmail !== "dev@firbyai.com" && !isOnboarded) {
      router.replace("/onboarding");
      return;
    }

    // 1. Bypass session gate in DEV environment for anonymous dev exploration
    const isDev = typeof window !== "undefined" && (
      localStorage.getItem("firby_dev_mode") === "true" ||
      localStorage.getItem("firby_dev_bypass") === "true" ||
      ((window.location.hostname.includes("dev.") || window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") && !userEmail)
    );

    if (isDev) {
      if (!localStorage.getItem("firby_master_key")) {
        localStorage.setItem("firby_master_key", "dev_master_key_preview");
      }
      if (!localStorage.getItem("firby_user_name")) {
        localStorage.setItem("firby_user_name", "Desarrollador Firby");
      }
      if (!localStorage.getItem("firby_user_email")) {
        localStorage.setItem("firby_user_email", "dev@firbyai.com");
      }
      setReady(true);
      return;
    }

    // 2. Production check
    const actualKeys = [...allowedKeys, "firby_master_key", "conny_master_key"];
    const hasAccess = actualKeys.some((key) => localStorage.getItem(key));
    if (!hasAccess) {
      router.replace(redirectTo);
      return;
    }

    if (!isOnboarded) {
      router.replace("/onboarding");
      return;
    }

    setReady(true);
  }, [allowedKeys, redirectTo, router]);

  if (!ready) {
    return (
      <div className="min-h-screen bg-[#fafafa] dark:bg-[#0a0a0c] flex items-center justify-center px-4">
        <Loader2 className="w-8 h-8 text-[#e05a2b] animate-spin" />
      </div>
    );
  }

  return <>{children}</>;
}
