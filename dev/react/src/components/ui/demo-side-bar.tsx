"use client";
import React, { useState, useEffect } from 'react';
import Link from "next/link";
import { usePathname, useRouter } from 'next/navigation';
import {
  Home,
  Settings,
  History,
  Link as LinkIcon,
  Zap,
  ChevronLeft,
  Menu,
  PanelLeftClose
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface NavigationItem {
  id: string;
  name: string;
  icon: React.ComponentType<{ className?: string }>;
  href: string;
  badge?: string;
}

const navigationItems: NavigationItem[] = [
  { id: "chat", name: "New Chat", icon: Home, href: "/demo" },
  { id: "history", name: "History", icon: History, href: "#" },
  { id: "connections", name: "Connections", icon: LinkIcon, href: "#" },
  { id: "auto_improve", name: "Auto-improve", icon: Zap, href: "#" },
  { id: "settings", name: "Settings", icon: Settings, href: "/settings" },
];

export function DemoSidebar({ className = "", children }: any) {
  const [isCollapsed, setIsCollapsed] = useState(true);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [activeItem, setActiveItem] = useState("chat");
  const [profile, setProfile] = useState<any>({ name: "Santiago", email: "santi21435@gmail.com", avatar: "" });
  const [sidebarWidth, setSidebarWidth] = useState(260);
  const [isDragging, setIsDragging] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem("firby_master_key") || localStorage.getItem("dev_master_key") || "";
        const res = await fetch("/api/user/profile", { headers: { "x-master-key": token } });
        if (res.ok) {
          const data = await res.json();
          setProfile(data);
        }
      } catch (e) {}
    };
    fetchProfile();
    
    const handleResize = () => {
      if (window.innerWidth < 768) {
        setIsCollapsed(false); 
      } else {
        setIsMobileOpen(false);
      }
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleItemClick = (itemId: string, href: string) => {
    if (href && href !== "#") {
        router.push(href);
    }
    setActiveItem(itemId);
    if (window.innerWidth < 768) {
        setIsMobileOpen(false);
    }
  };

  
  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
    const startX = e.clientX;
    const startWidth = sidebarWidth;

    const onMouseMove = (moveEvent: MouseEvent) => {
      const newWidth = startWidth + (moveEvent.clientX - startX);
      setSidebarWidth(Math.min(400, Math.max(160, newWidth)));
    };

    const onMouseUp = () => {
      setIsDragging(false);
      document.removeEventListener("mousemove", onMouseMove);
      document.removeEventListener("mouseup", onMouseUp);
    };

    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("mouseup", onMouseUp);
  };

  const SidebarContent = () => (
    <>
      <div 
        className={`flex items-center ${isCollapsed ? "flex-col py-5" : "justify-between p-5"} border-b border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-[#111111]/60`}
      >
        {!isCollapsed && (
          <div className="flex items-center space-x-3">
            <div className="h-8 rounded-lg flex items-center justify-center">
              
              <img src="/brand-assets/isotipo_firby_plano_verde_lima.png" alt="Firby" className="h-full w-auto object-contain" />
            </div>
            <div className="flex flex-col">
              <span className="font-semibold text-neutral-900 dark:text-white text-sm">{profile.name}</span>
              <span className="text-[10px] text-neutral-500 dark:text-neutral-600 dark:text-neutral-400">Workspace</span>
            </div>
          </div>
        )}
        
        {isCollapsed && (
            <div className="h-8 rounded-lg flex items-center justify-center hover:scale-105 transition-transform mb-4" title="Expand Sidebar">
              <img src="/brand-assets/isotipo_firby_plano_verde_lima.png" alt="Firby" className="h-full w-auto object-contain" />
            </div>
        )}

        {!isCollapsed && (
        <button 
            onClick={(e) => { e.stopPropagation(); setIsCollapsed(true); }}
            className={`p-1.5 rounded-md text-neutral-500 hover:bg-neutral-200 dark:hover:bg-neutral-800 transition-colors`}
            title="Collapse Sidebar"
        >
            <PanelLeftClose className="w-5 h-5 text-neutral-700 dark:text-neutral-300" />
        </button>
        )}
      </div>

      <div className="flex flex-col flex-1 overflow-hidden">
        <nav className={`flex-1 ${isCollapsed ? "px-2" : "px-3"} py-4 overflow-y-auto custom-scrollbar`}>
          <ul className="space-y-2">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeItem === item.id;

              return (
                <li key={item.id}>
                  <button
                    onClick={() => handleItemClick(item.id, item.href)}
                    className={`
                      w-full flex items-center py-2 transition-all duration-150 group border-l-2
                      ${isCollapsed ? "justify-center rounded-md px-0" : "space-x-3 rounded-r-md pl-[10px] pr-3"}
                      ${isActive
                        ? "border-[#e05a2b] text-[#e05a2b] bg-neutral-100 dark:bg-white/5"
                        : "border-transparent text-neutral-600 dark:text-[#666666] hover:bg-neutral-100 dark:hover:bg-white/5"
                      }
                    `}
                    title={isCollapsed ? item.name : undefined}
                  >
                    <div className="flex items-center justify-center min-w-[24px]">
                      <Icon className={`h-5 w-5 flex-shrink-0 ${isActive ? "text-[#e05a2b]" : "text-neutral-500 dark:text-[#666666] group-hover:text-neutral-700 dark:group-hover:text-white"}`} />
                    </div>

                    {!isCollapsed && (
                      <div className="flex items-center justify-between w-full">
                        <span className={`text-sm ${isActive ? "font-medium" : "font-normal"}`}>{item.name}</span>
                      </div>
                    )}
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Bottom section */}
        <div className={`mt-auto pb-6 flex flex-col pt-4 border-t border-neutral-200 dark:border-neutral-800/50 ${isCollapsed ? "gap-4 items-center px-1" : "gap-5 px-4"}`}>
          <div 
            onClick={() => handleItemClick('settings', '/settings/')}
            className={`flex items-center cursor-pointer group ${isCollapsed ? "justify-center" : "justify-start"}`}
            title="Settings & Profile"
          >
            <div className="h-8 w-8 rounded-full overflow-hidden flex items-center justify-center flex-shrink-0 shadow-sm border border-neutral-200 dark:border-[#333]">
                {profile.avatar ? <img src={profile.avatar} className="w-full h-full object-cover" /> : <span className="font-bold text-neutral-600 dark:text-[#ccc] text-sm">{profile.name?.charAt(0)}</span>}
            </div>
            
            {!isCollapsed && (
              <div className="ml-3 flex flex-col min-w-0">
                <span className={`text-sm font-semibold truncate transition-colors text-neutral-900 dark:text-white group-hover:text-[#e05a2b]`}>{profile.name}</span>
                <span className="text-xs text-neutral-500 dark:text-neutral-400 truncate">{profile.email}</span>
              </div>
            )}
          </div>
          
          <Link
            href="/panel/"
            className={`flex items-center cursor-pointer group transition-colors ${isCollapsed ? "justify-center" : "justify-start"} text-neutral-500 hover:text-neutral-900 dark:hover:text-white`}
            title={isCollapsed ? "Back to Main" : undefined}
          >
            <ChevronLeft className="h-4 w-4 flex-shrink-0" />
            {!isCollapsed && <span className="ml-3 text-xs font-medium">Back to Main</span>}
          </Link>

        </div>
      </div>
    </>
  );

  return (
    <>
      <button
        onClick={() => setIsMobileOpen(true)}
        className="fixed top-4 left-4 z-40 p-2 rounded-md bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 md:hidden hover:bg-neutral-200 dark:hover:bg-neutral-800 transition-all duration-200"
      >
        <Menu className="h-5 w-5 text-neutral-700 dark:text-neutral-300" />
      </button>

      <AnimatePresence>
        {isMobileOpen && (
          <>
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 md:hidden transition-opacity" 
              onClick={() => setIsMobileOpen(false)} 
            />
            <motion.aside
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className="fixed inset-y-0 left-0 bg-neutral-50 dark:bg-[#111111] border-r border-neutral-200 dark:border-neutral-800 z-50 flex flex-col w-[260px]"
            >
              <div className="flex items-center justify-between p-5 border-b border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-[#111111]/60">
                <div className="flex items-center space-x-3">
                  <div className="h-8 rounded-lg flex items-center justify-center">
                    
              <img src="/brand-assets/isotipo_firby_plano_verde_lima.png" alt="Firby" className="h-full w-auto object-contain" />
                  </div>
                  <div className="flex flex-col">
                    <span className="font-semibold text-neutral-900 dark:text-white text-sm">{profile.name}</span>
                    <span className="text-[10px] text-neutral-500 dark:text-neutral-600 dark:text-neutral-400">Workspace</span>
                  </div>
                </div>
                <button onClick={() => setIsMobileOpen(false)} className="p-1.5 rounded-md text-neutral-500 hover:bg-neutral-200 dark:hover:bg-neutral-800 transition-colors">
                    <PanelLeftClose className="w-5 h-5 text-neutral-700 dark:text-neutral-300" />
                </button>
              </div>

              <div className="flex flex-col flex-1 overflow-hidden">
                <nav className="flex-1 px-3 py-4 overflow-y-auto custom-scrollbar">
                  <ul className="space-y-2">
                    {navigationItems.map((item) => {
                      const Icon = item.icon;
                      const isActive = activeItem === item.id;
                      return (
                        <li key={item.id}>
                          <button
                            onClick={() => handleItemClick(item.id, item.href)}
                            className={`w-full flex items-center py-2 transition-all duration-150 group border-l-2 space-x-3 rounded-r-md pl-[10px] pr-3 ${isActive ? "border-[#e05a2b] text-[#e05a2b] bg-neutral-100 dark:bg-white/5" : "border-transparent text-neutral-600 dark:text-[#666666] hover:bg-neutral-100 dark:hover:bg-white/5"}`}
                          >
                            <div className="flex items-center justify-center min-w-[24px]">
                              <Icon className={`h-5 w-5 flex-shrink-0 ${isActive ? "text-[#e05a2b]" : "text-neutral-500 dark:text-[#666666] group-hover:text-neutral-700 dark:group-hover:text-white"}`} />
                            </div>
                            <span className={`text-sm ${isActive ? "font-medium" : "font-normal"}`}>{item.name}</span>
                          </button>
                        </li>
                      );
                    })}
                  </ul>
                </nav>
                <div className="mt-auto pb-6 flex flex-col pt-4 border-t border-neutral-200 dark:border-neutral-800/50 gap-5 px-4">
                  <div onClick={() => handleItemClick('settings', '/settings/')} className="flex items-center cursor-pointer group justify-start">
                    <div className="h-8 w-8 rounded-full overflow-hidden flex items-center justify-center flex-shrink-0 shadow-sm border border-neutral-200 dark:border-[#333]">
                        {profile.avatar ? <img src={profile.avatar} className="w-full h-full object-cover" /> : <span className="font-bold text-neutral-600 dark:text-[#ccc] text-sm">{profile.name?.charAt(0)}</span>}
                    </div>
                    <div className="ml-3 flex flex-col min-w-0">
                      <span className="text-sm font-semibold truncate transition-colors text-neutral-900 dark:text-white group-hover:text-[#e05a2b]">{profile.name}</span>
                      <span className="text-xs text-neutral-500 dark:text-neutral-400 truncate">{profile.email}</span>
                    </div>
                  </div>
                  <Link href="/panel/" className="flex items-center cursor-pointer group transition-colors justify-start text-neutral-500 hover:text-neutral-900 dark:hover:text-white">
                    <ChevronLeft className="h-4 w-4 flex-shrink-0" />
                    <span className="ml-3 text-xs font-medium">Back to Main</span>
                  </Link>
                </div>
              </div>
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      <motion.aside
        animate={{ width: isCollapsed ? 70 : sidebarWidth }}
        transition={isDragging ? { duration: 0 } : { type: "spring", damping: 25, stiffness: 200 }}
        className={`hidden md:flex flex-col bg-neutral-50 dark:bg-[#111111] border-r border-neutral-200 dark:border-neutral-800 z-30 flex-shrink-0 h-screen overflow-hidden relative`}
      >
        <SidebarContent />
        {!isCollapsed && (
            <div
              onMouseDown={handleMouseDown}
              onDoubleClick={() => setSidebarWidth(260)}
              className="absolute right-0 top-0 w-1.5 h-full cursor-col-resize z-50 hover:bg-[#e05a2b]/30 transition-colors"
            />
        )}
      </motion.aside>
    </>
  );
}
