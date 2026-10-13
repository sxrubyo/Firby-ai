"use client";
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from "framer-motion";
import { usePathname, useRouter } from 'next/navigation';
import {
  Home,
  MessageSquare,
  Kanban,
  Library,
  FlaskConical,
  Brain,
  Settings,
  Menu,
  X,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  ShieldCheck,
  PanelLeftClose
} from 'lucide-react';

interface NavigationItem {
  id: string;
  name: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
  badgeColor?: string;
}

interface WorkspaceSidebarProps {
  activeTab: string;
  onTabChange: (tabId: any) => void;
  initialCollapsed?: boolean;
}

const navigationItems: NavigationItem[] = [
  { id: "overview", name: "Panel General", icon: Home },
  { id: "inbox", name: "Bandeja En Vivo", icon: MessageSquare, badge: "3" },
  { id: "kanban", name: "Pipeline de Ventas", icon: Kanban },
  { id: "library", name: "Biblioteca Media", icon: Library, badge: "PRO", badgeColor: "bg-amber-500/20 text-amber-400" },
  { id: "laboratory", name: "Laboratorio 0-100", icon: FlaskConical, badge: "94%", badgeColor: "bg-emerald-500/20 text-emerald-400" },
  { id: "knowledge", name: "Conocimiento & Prompt", icon: Brain },
  { id: "settings", name: "Configuración", icon: Settings },
];

export function WorkspaceSidebar({ activeTab, onTabChange, initialCollapsed = false }: WorkspaceSidebarProps) {
  const [profile, setProfile] = useState<any>({ name: "Clínica Admin", email: "admin@firby.ai", avatar: "" });
  const [isCollapsed, setIsCollapsed] = useState(initialCollapsed);
  const [sidebarWidth, setSidebarWidth] = useState(260);
  const [isDragging, setIsDragging] = useState(false);
  const [isOpen, setIsOpen] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem("firby_master_key") || localStorage.getItem("dev_master_key") || "";
        const res = await fetch("/api/user/profile", { headers: { "x-master-key": token } });
        if (res.ok) {
          const data = await res.json();
          setProfile((prev: any) => ({ ...prev, ...data }));
        }
      } catch (e) {}
    };
    fetchProfile();
  }, []);

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
    const startX = e.clientX;
    const startWidth = sidebarWidth;

    const onMouseMove = (moveEvent: MouseEvent) => {
      const newWidth = startWidth + (moveEvent.clientX - startX);
      setSidebarWidth(Math.min(380, Math.max(180, newWidth)));
    };

    const onMouseUp = () => {
      setIsDragging(false);
      document.removeEventListener("mousemove", onMouseMove);
      document.removeEventListener("mouseup", onMouseUp);
    };

    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("mouseup", onMouseUp);
  };

  return (
    <>
      {/* Mobile Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="md:hidden fixed top-4 left-4 z-50 p-2.5 bg-[#252525] text-white rounded-xl border border-[#333] shadow-lg"
      >
        {isOpen ? <X className="size-5" /> : <Menu className="size-5" />}
      </button>

      {/* Main Sidebar Component */}
      <aside
        style={{ width: isCollapsed ? 76 : sidebarWidth }}
        className={`fixed md:relative top-0 left-0 h-full bg-[#181818] dark:bg-[#181818] border-r border-[#2e2e2e] dark:border-[#2e2e2e] flex flex-col justify-between z-40 transition-all duration-300 select-none ${
          isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        } ${isDragging ? "transition-none" : ""}`}
      >
        {/* Resize Handle */}
        <div
          onMouseDown={handleMouseDown}
          className="hidden md:block absolute top-0 right-0 w-1.5 h-full cursor-col-resize hover:bg-amber-500/50 transition-colors z-50"
        />

        {/* Top Header & Logo */}
        <div>
          <div className="p-4 border-b border-[#2e2e2e] flex items-center justify-between">
            <div 
              className="flex items-center gap-3 overflow-hidden cursor-pointer"
              onClick={() => isCollapsed && setIsCollapsed(false)}
              title={isCollapsed ? "Expandir barra lateral" : undefined}
            >
              <img src="/brand-assets/Isotipo-pestaña.png" alt="Firby" className="h-8 w-auto object-contain" />
              {!isCollapsed && (
                <span className="text-[10px] uppercase font-bold tracking-wider text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                  Workspace
                </span>
              )}
            </div>
            <button
              onClick={() => setIsCollapsed(!isCollapsed)}
              className="hidden md:flex p-1.5 rounded-lg text-neutral-400 hover:text-white hover:bg-[#252525] transition-colors"
            >
              {isCollapsed ? <ChevronRight className="size-4" /> : <ChevronLeft className="size-4" />}
            </button>
          </div>

          {/* Online Status Badge */}
          {!isCollapsed && (
            <div className="p-3 mx-3 my-3 bg-[#222222] border border-[#2e2e2e] rounded-xl flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="relative flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                </span>
                <span className="text-xs font-medium text-neutral-200">WhatsApp Conectado</span>
              </div>
              <ShieldCheck className="size-4 text-emerald-400" />
            </div>
          )}

          {/* Navigation Links */}
          <nav className="p-2 space-y-1 mt-1">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onTabChange(item.id)}
                  title={isCollapsed ? item.name : undefined}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${
                    isActive
                      ? "bg-[#282828] text-white border border-[#383838] shadow-sm shadow-black/20"
                      : "text-neutral-400 hover:bg-[#202020] hover:text-white"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`size-4 ${isActive ? "text-amber-400" : ""}`} />
                    {!isCollapsed && <span>{item.name}</span>}
                  </div>
                  {!isCollapsed && item.badge && (
                    <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${item.badgeColor || "bg-[#333] text-neutral-300"}`}>
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* User Profile Footer */}
        <div className="p-3 border-t border-[#2e2e2e] space-y-2">
          <div className="flex items-center gap-3 p-2 rounded-xl bg-[#222222] border border-[#2e2e2e]">
            <div className="w-8 h-8 rounded-full bg-neutral-800 border border-neutral-700 flex items-center justify-center shrink-0 overflow-hidden">
              <img src="/brand-assets/Isotipo-pestaña.png" alt="Firby" className="size-6 object-contain" />
            </div>
            {!isCollapsed && (
              <div className="flex flex-col text-left overflow-hidden flex-1">
                <span className="text-xs font-semibold text-white truncate">{profile.name || "Administración"}</span>
                <span className="text-[10px] text-neutral-400 truncate">{profile.email || "admin@firby.ai"}</span>
              </div>
            )}
          </div>
        </div>
      </aside>
    </>
  );
}
