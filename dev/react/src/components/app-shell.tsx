"use client";

import React, { useState, useEffect, useContext } from "react";
import { Sidebar } from "@/components/ui/modern-side-bar";
import { PanelLeft, User, CreditCard, LogOut, Sun, Moon } from "lucide-react";
import { ThemeContext } from "@/components/theme-provider";
import * as Popover from "@radix-ui/react-popover";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { playSound } from "@/lib/sound";

interface WorkspaceNotification {
  id: string;
  title: string;
  message: string;
  type?: string;
  time?: string;
  timestamp?: number;
  read?: boolean;
}

interface AppShellProps {
  children: React.ReactNode;
  fullWidth?: boolean;
  noPadding?: boolean;
  className?: string;
  headerSlot?: React.ReactNode;
}

export function AppShell({
  children,
  fullWidth = false,
  noPadding = false,
  className = "",
  headerSlot,
}: AppShellProps) {
  const router = useRouter();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const { isDark, toggleDark } = useContext(ThemeContext);

  const [notifications, setNotifications] = useState<WorkspaceNotification[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [toastNotif, setToastNotif] = useState<WorkspaceNotification | null>(null);
  const lastSeenNotifIdRef = React.useRef<string | null>(null);
  const isFirstFetchRef = React.useRef<boolean>(true);

  const [profile, setProfile] = useState<{ name: string; email: string; avatar: string }>(() => {
    if (typeof window !== "undefined") {
      const email = localStorage.getItem("firby_user_email") || "";
      const name = localStorage.getItem("firby_user_name") || (email ? email.split("@")[0] : "");
      const avatar = localStorage.getItem("firby_user_avatar") || "";
      return { name, email, avatar };
    }
    return { name: "", email: "", avatar: "" };
  });

  useEffect(() => {
    try {
      const saved = localStorage.getItem("firby_sidebar_collapsed");
      if (saved !== null) {
        setIsSidebarCollapsed(saved === "true");
      }
    } catch (_) {}
  }, []);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem("firby_master_key") || localStorage.getItem("dev_master_key") || "";
        const email = localStorage.getItem("firby_user_email") || "";
        const res = await fetch("/api/user/profile", {
          headers: {
            "x-master-key": token,
            "x-user-email": email,
          },
        });
        if (res.ok) {
          const data = await res.json();
          if (data && data.name) {
            setProfile((prev) => ({
              ...prev,
              name: data.name || prev.name,
              email: data.email || prev.email,
              avatar: data.avatar || prev.avatar,
            }));
            localStorage.setItem("firby_user_name", data.name);
            if (data.email) localStorage.setItem("firby_user_email", data.email);
            if (data.avatar) localStorage.setItem("firby_user_avatar", data.avatar);
          }
        }
      } catch (_) {}
    };
    fetchProfile();

    const handleProfileUpdate = (e: any) => {
      if (e.detail?.name) setProfile((prev) => ({ ...prev, name: e.detail.name }));
      if (e.detail?.email) setProfile((prev) => ({ ...prev, email: e.detail.email }));
      if (e.detail?.avatar) setProfile((prev) => ({ ...prev, avatar: e.detail.avatar }));
    };

    window.addEventListener("profileUpdated", handleProfileUpdate);
    return () => window.removeEventListener("profileUpdated", handleProfileUpdate);
  }, []);

  useEffect(() => {
    let isMounted = true;

    const fetchNotifications = async () => {
      try {
        const res = await fetch("/api/workspace/notifications?limit=20");
        if (!res.ok) return;
        const data = await res.json();
        if (!isMounted || !data.ok) return;

        const notifs: WorkspaceNotification[] = data.notifications || [];
        const unread = typeof data.unread_count === "number" ? data.unread_count : 0;
        const latest = data.latest;

        setNotifications(notifs);
        setUnreadCount(unread);

        if (latest && latest.id) {
          if (isFirstFetchRef.current) {
            isFirstFetchRef.current = false;
            lastSeenNotifIdRef.current = latest.id;
          } else if (latest.id !== lastSeenNotifIdRef.current) {
            lastSeenNotifIdRef.current = latest.id;
            playSound("pop");
            setToastNotif(latest);
            setTimeout(() => {
              if (isMounted) setToastNotif((prev) => (prev?.id === latest.id ? null : prev));
            }, 6500);
          }
        } else {
          isFirstFetchRef.current = false;
        }
      } catch (_) {}
    };

    fetchNotifications();
    const interval = setInterval(fetchNotifications, 2500);

    const handleNotificationArrival = (e: any) => {
      playSound("pop");
      if (e?.detail) {
        const custom: WorkspaceNotification = {
          id: `custom_${Date.now()}`,
          title: e.detail.title || "Notificación de Firby",
          message: e.detail.message || "Nueva actividad en el agente de IA.",
          time: "Justo ahora",
          read: false,
        };
        setNotifications((prev) => [custom, ...prev]);
        setUnreadCount((c) => c + 1);
        setToastNotif(custom);
        setTimeout(() => {
          if (isMounted) setToastNotif((prev) => (prev?.id === custom.id ? null : prev));
        }, 6500);
      }
    };

    window.addEventListener("firby:notify", handleNotificationArrival);
    window.addEventListener("firby:notification", handleNotificationArrival);
    return () => {
      isMounted = false;
      clearInterval(interval);
      window.removeEventListener("firby:notify", handleNotificationArrival);
      window.removeEventListener("firby:notification", handleNotificationArrival);
    };
  }, []);

  const markAllNotificationsRead = async () => {
    try {
      setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
      setUnreadCount(0);
      await fetch("/api/workspace/notifications/mark-all-read", { method: "POST" });
    } catch (_) {}
  };

  const handleLogout = () => {
    try {
      localStorage.removeItem("firby_master_key");
      localStorage.removeItem("dev_master_key");
      localStorage.removeItem("firby_dev_mode");
      localStorage.removeItem("firby_user_email");
      localStorage.removeItem("firby_user_name");
      localStorage.removeItem("firby_user_avatar");
      localStorage.removeItem("firby_auth_provider");
      localStorage.removeItem("firby_onboarding_done");
    } catch (_) {}
    router.replace("/sign-in");
  };

  const userInitials = profile.name
    ? profile.name
        .split(" ")
        .map((n) => n[0])
        .slice(0, 2)
        .join("")
        .toUpperCase()
    : "S";

  const handleToggleSidebar = () => {
    if (typeof window !== "undefined" && window.innerWidth < 768) {
      setMobileMenuOpen((prev) => !prev);
      return;
    }
    setIsSidebarCollapsed((prev) => {
      const next = !prev;
      try {
        localStorage.setItem("firby_sidebar_collapsed", String(next));
      } catch (_) {}
      return next;
    });
  };

  return (
    <div className="flex flex-col h-screen w-full bg-[#F9F3F2] dark:bg-[#0e0e11] font-sans text-neutral-900 dark:text-neutral-100 overflow-hidden">
      
      {/* 1. HEADER DE EXTREMO A EXTREMO: BLANCO EN MODO CLARO / NEGRO EN MODO OSCURO */}
      <header className="w-full h-16 bg-white dark:bg-[#000000] border-b border-neutral-200 dark:border-[#1a1a1f] px-4 sm:px-10 flex items-center justify-between shrink-0 select-none z-40 shadow-[0_1px_4px_rgba(0,0,0,0.05)] dark:shadow-[0_4px_24px_rgba(0,0,0,0.65)] relative">
        <div className="w-full flex items-center justify-between">
          <div className="flex items-center gap-3">
            <a
              href="/workspace/"
              title="Volver al inicio"
              className="inline-flex items-center ml-3 transition-transform hover:scale-[1.02] active:scale-[0.98] cursor-pointer"
            >
              <img
                src="/assets/figma/firby_brand_logo.png"
                alt="Firby AI"
                className="h-7 sm:h-8 w-auto object-contain select-none dark:hidden"
              />
              <img
                src="/assets/figma/firby_brand_logo_dark.png"
                alt="Firby AI"
                className="h-7 sm:h-8 w-auto object-contain select-none hidden dark:block"
              />
            </a>

            {/* BOTÓN DE COLAPSAR / EXPANDIR SIDEBAR A LA DERECHA DEL ISOTIPO */}
            <button
              type="button"
              onClick={handleToggleSidebar}
              className="inline-flex items-center justify-center p-2 rounded-lg transition-colors cursor-pointer group bg-transparent hover:bg-transparent text-neutral-500 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-white shrink-0"
              title={isSidebarCollapsed ? "Expandir barra lateral" : "Contraer barra lateral"}
              aria-label={isSidebarCollapsed ? "Expandir barra lateral" : "Contraer barra lateral"}
            >
              <PanelLeft
                className="w-4 h-4 text-neutral-600 dark:text-neutral-300 group-hover:text-black dark:group-hover:text-white transition-colors"
                strokeWidth={1.8}
              />
            </button>

            {/* SLOT PARA BREADCRUMB / TÍTULO DE CONTEXTO SUPERIOR (OCULTO EN MÓVIL PARA EVITAR DESBORDAMIENTO) */}
            {headerSlot && (
              <div className="hidden md:flex items-center ml-2 pl-3 border-l border-neutral-200 dark:border-white/10 min-w-0">
                {headerSlot}
              </div>
            )}
          </div>

          {/* CONTROLES ESQUINA DERECHA: NOTIFICACIONES Y TEMA (SIN FONDO, ICONOS PREMIUM) */}
          <div className="flex items-center gap-1 sm:gap-1.5">
            {/* 1. BOTÓN DE NOTIFICACIONES */}
            <Popover.Root>
              <Popover.Trigger asChild>
                <button
                  type="button"
                  onClick={() => playSound("perk")}
                  className="relative p-2 rounded-lg bg-transparent text-neutral-600 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-white transition-colors cursor-pointer group flex items-center justify-center"
                  title="Notificaciones"
                  aria-label="Notificaciones"
                >
                  <svg
                    viewBox="0 0 24 24"
                    width="19"
                    height="19"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.7"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="transition-transform duration-200 group-hover:scale-105"
                  >
                    <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
                    <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
                  </svg>
                  {/* Puntero sutil de actividad */}
                  {unreadCount > 0 ? (
                    <span className="absolute top-1.5 right-1.5 size-2 rounded-full bg-[#84cc16] dark:bg-[#b9fa01] ring-2 ring-white dark:ring-black animate-pulse" />
                  ) : (
                    <span className="absolute top-1.5 right-1.5 size-1.5 rounded-full bg-neutral-300 dark:bg-neutral-600" />
                  )}
                </button>
              </Popover.Trigger>
              <Popover.Portal>
                <Popover.Content
                  sideOffset={8}
                  align="end"
                  className="z-50 w-84 max-w-[90vw] rounded-2xl bg-white dark:bg-[#141418] border border-neutral-200 dark:border-[#27272a] p-4 text-neutral-900 dark:text-neutral-100 shadow-2xl focus:outline-hidden"
                >
                  <div className="flex items-center justify-between pb-3 border-b border-neutral-100 dark:border-[#22222a]">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold uppercase tracking-wider text-neutral-500 dark:text-neutral-300 font-mono">
                        Notificaciones
                      </span>
                      {unreadCount > 0 && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-lime-100 dark:bg-[#b9fa01]/10 text-lime-800 dark:text-[#b9fa01] font-mono font-semibold">
                          {unreadCount}
                        </span>
                      )}
                    </div>
                    {unreadCount > 0 ? (
                      <button
                        type="button"
                        onClick={markAllNotificationsRead}
                        className="text-[10px] font-mono font-medium text-neutral-500 hover:text-black dark:text-neutral-400 dark:hover:text-[#b9fa01] transition-colors cursor-pointer"
                      >
                        Marcar leídas
                      </button>
                    ) : (
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-neutral-100 dark:bg-neutral-800 text-neutral-500 dark:text-neutral-400 font-mono font-medium">
                        Al día
                      </span>
                    )}
                  </div>

                  {notifications.length === 0 ? (
                    <div className="py-6 text-center space-y-1">
                      <p className="text-xs font-medium text-neutral-900 dark:text-neutral-200">
                        Sin notificaciones pendientes
                      </p>
                      <p className="text-[11px] text-neutral-500">
                        Tu agente de IA está activo y respondiendo a tus pacientes.
                      </p>
                    </div>
                  ) : (
                    <div className="py-2 max-h-72 overflow-y-auto space-y-2 divide-y divide-neutral-100 dark:divide-[#22222a]/60">
                      {notifications.slice(0, 6).map((notif) => (
                        <div key={notif.id} className="pt-2 first:pt-0 flex items-start gap-2.5">
                          <span
                            className={`mt-1 size-2 rounded-full shrink-0 ${
                              notif.read ? "bg-neutral-300 dark:bg-neutral-700" : "bg-[#84cc16] dark:bg-[#b9fa01]"
                            }`}
                          />
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between gap-1">
                              <h4 className="text-xs font-semibold text-neutral-900 dark:text-white truncate">
                                {notif.title}
                              </h4>
                              <span className="text-[9px] text-neutral-400 font-mono shrink-0">
                                {notif.time || "Reciente"}
                              </span>
                            </div>
                            <p className="text-[11px] text-neutral-600 dark:text-neutral-300 line-clamp-2 mt-0.5 leading-snug">
                              {notif.message}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </Popover.Content>
              </Popover.Portal>
            </Popover.Root>

            {/* 2. PERFIL DE USUARIO ARRIBA (ANILLO PREMIUM ESTILO GOOGLE ONE EN VERDE LIMA Y AMARILLO) */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button
                  type="button"
                  className="group relative inline-flex items-center justify-center p-[2px] rounded-full transition-all duration-300 hover:scale-105 active:scale-95 cursor-pointer outline-hidden ml-1 hover:shadow-[0_0_14px_rgba(185,250,1,0.45)]"
                  style={{
                    background: "conic-gradient(from 215deg, #b9fa01 0%, #facc15 32%, #eab308 52%, #84cc16 78%, #b9fa01 100%)",
                  }}
                  aria-label="Perfil de usuario"
                  title={profile.name || "Perfil"}
                >
                  {/* Halo sutil ambiental */}
                  <span
                    className="absolute inset-0 rounded-full blur-[3px] opacity-30 group-hover:opacity-70 transition-opacity duration-300 pointer-events-none"
                    style={{
                      background: "conic-gradient(from 215deg, #b9fa01 0%, #facc15 32%, #eab308 52%, #84cc16 78%, #b9fa01 100%)",
                    }}
                  />
                  {/* Gap interior estilo Google One (espacio blanco / negro puro) */}
                  <div className="relative p-[2px] rounded-full bg-white dark:bg-[#000000] flex items-center justify-center transition-colors">
                    {profile.avatar ? (
                      <img
                        src={profile.avatar}
                        alt={profile.name}
                        className="size-7 sm:size-8 rounded-full object-cover"
                      />
                    ) : (
                      <div className="size-7 sm:size-8 rounded-full bg-neutral-100 dark:bg-neutral-800 text-neutral-800 dark:text-white flex items-center justify-center font-bold text-[11px]">
                        {userInitials}
                      </div>
                    )}
                  </div>
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                align="end"
                sideOffset={8}
                className="w-56 p-1.5 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#18181b] text-neutral-900 dark:text-neutral-100 shadow-xl z-50"
              >
                <div className="px-2.5 py-2 border-b border-neutral-100 dark:border-neutral-800 mb-1 flex items-center gap-2.5">
                  <div
                    className="p-[2px] rounded-full shrink-0"
                    style={{
                      background: "conic-gradient(from 215deg, #b9fa01 0%, #facc15 32%, #eab308 52%, #84cc16 78%, #b9fa01 100%)",
                    }}
                  >
                    <div className="p-[1.5px] rounded-full bg-white dark:bg-[#18181b] flex items-center justify-center">
                      {profile.avatar ? (
                        <img
                          src={profile.avatar}
                          alt={profile.name}
                          className="size-8 rounded-full object-cover shrink-0"
                        />
                      ) : (
                        <div className="size-8 rounded-full bg-neutral-100 dark:bg-neutral-800 text-neutral-800 dark:text-neutral-200 flex items-center justify-center font-bold text-xs shrink-0">
                          {userInitials}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex flex-col min-w-0">
                    <p className="text-xs font-semibold text-neutral-900 dark:text-white truncate">{profile.name}</p>
                    <p className="text-[11px] text-neutral-500 dark:text-neutral-400 truncate">{profile.email}</p>
                  </div>
                </div>
                <DropdownMenuItem
                  onClick={() => router.push("/settings/")}
                  className="text-xs cursor-pointer gap-2 px-2.5 py-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-white/5"
                >
                  <User className="h-4 w-4 text-neutral-500 dark:text-neutral-400" />
                  <span>Perfil</span>
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => router.push("/settings/")}
                  className="text-xs cursor-pointer gap-2 px-2.5 py-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-white/5"
                >
                  <CreditCard className="h-4 w-4 text-neutral-500 dark:text-neutral-400" />
                  <span>Facturación</span>
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={toggleDark}
                  className="text-xs cursor-pointer gap-2 px-2.5 py-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-white/5"
                >
                  {isDark ? (
                    <>
                      <Sun className="h-4 w-4 text-amber-400" />
                      <span>Modo claro</span>
                    </>
                  ) : (
                    <>
                      <Moon className="h-4 w-4 text-neutral-500" />
                      <span>Modo oscuro</span>
                    </>
                  )}
                </DropdownMenuItem>
                <DropdownMenuSeparator className="my-1 border-neutral-200 dark:border-neutral-800" />
                <DropdownMenuItem
                  onClick={handleLogout}
                  className="text-xs text-red-600 dark:text-red-400 cursor-pointer gap-2 px-2.5 py-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-950/20"
                >
                  <LogOut className="h-4 w-4" />
                  <span>Cerrar sesión</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      {/* 2. ÁREA INFERIOR: COLOR DE LA PÁGINA CON SIDEBAR DESKTOP + CONTENIDO FULL WIDTH EN MÓVIL */}
      <div className="flex flex-1 min-h-0 w-full overflow-hidden bg-[#F9F3F2] dark:bg-[#0e0e11] relative">
        <Sidebar
          isCollapsed={isSidebarCollapsed}
          onToggleCollapse={handleToggleSidebar}
          isMobileOpen={mobileMenuOpen}
          onCloseMobile={() => setMobileMenuOpen(false)}
        />
        <main
          className={`flex-1 min-w-0 bg-[#F9F3F2] dark:bg-[#0e0e11] w-full ${
            noPadding ? "overflow-hidden flex flex-col" : "overflow-y-auto"
          } ${className}`}
        >
          {noPadding ? (
            children
          ) : (
            <div
              className={`p-4 sm:p-6 lg:py-8 w-full ${
                fullWidth ? "max-w-[1800px] lg:px-8" : "max-w-7xl lg:px-8"
              } mx-auto`}
            >
              {children}
            </div>
          )}
        </main>
      </div>

      {/* TOAST DE NOTIFICACIÓN FLOTANTE */}
      <AnimatePresence>
        {toastNotif && (
          <motion.div
            initial={{ opacity: 0, y: -20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -20, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            onClick={() => setToastNotif(null)}
            className="fixed top-5 right-5 z-50 max-w-sm w-full bg-white dark:bg-[#141418] border border-neutral-200 dark:border-[#27272a] rounded-2xl p-3.5 shadow-2xl shadow-black/20 flex items-start gap-3 cursor-pointer hover:border-lime-500/50 transition-colors select-none"
          >
            <div className="p-2 rounded-xl bg-lime-100 dark:bg-[#b9fa01]/10 text-lime-700 dark:text-[#b9fa01] shrink-0">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
                <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
              </svg>
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-1">
                <h4 className="text-xs font-bold text-neutral-900 dark:text-white truncate">
                  {toastNotif.title}
                </h4>
                <span className="text-[10px] text-neutral-400 font-mono">
                  {toastNotif.time || "Justo ahora"}
                </span>
              </div>
              <p className="text-[11px] text-neutral-600 dark:text-neutral-300 mt-0.5 line-clamp-2 leading-relaxed">
                {toastNotif.message}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
