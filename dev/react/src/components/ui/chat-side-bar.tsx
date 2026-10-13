"use client";
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from "framer-motion";
import { usePathname, useRouter } from 'next/navigation';
import { Home, User, Settings, LogOut, Menu, PanelLeftClose, X, ChevronLeft, ChevronRight, BarChart3, FileText, Bell, Search, Server, MessageSquare, Bot, Shield, Key, TerminalSquare, Plus } from 'lucide-react';

interface NavigationItem {
  id: string;
  name: string;
  icon: React.ComponentType<{ className?: string }>;
  href: string;
  badge?: string;
}

interface SidebarProps {
  className?: string;
  children?: React.ReactNode;
  isCollapsed?: boolean;
  initialCollapsed?: boolean;
  onToggleCollapse?: () => void;
  onSelectChat?: (chatId: string) => void;
}

const navigationItems: NavigationItem[] = [
  { id: "ia-config", name: "Personalizar", icon: Bot, href: "#" },
  { id: "security", name: "Seguridad", icon: Shield, href: "#" },
  { id: "api-keys", name: "API Keys", icon: Key, href: "#" },
  { id: "logs", name: "Logs", icon: TerminalSquare, href: "#" },
];

export function ChatSideBar({ className = "", children, initialCollapsed = false, onSelectChat }: SidebarProps) {

  const [profile, setProfile] = useState<any>({ name: "Santiago", email: "Santi21435@gmail.com", avatar: "" });
  const [isCollapsed, setIsCollapsed] = useState(initialCollapsed);
  const [sidebarWidth, setSidebarWidth] = useState(260);
  const [recentChats, setRecentChats] = useState<{title: string, date: string, chat_id: string}[]>([]);
  useEffect(() => {
    fetch('/api/dev/chats')
      .then(res => res.json())
      .then(data => {
        if (data.conversations && data.conversations.length > 0) {
          setRecentChats(data.conversations);
        }
      })
      .catch(() => setRecentChats([]));
  }, []);
  const [isDragging, setIsDragging] = useState(false);
  const [isDev, setIsDev] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      setIsDev(!!localStorage.getItem("dev_master_key"));
    }
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

    const handleAvatarUpdate = (e: any) => {
      setProfile((prev: any) => ({ ...prev, avatar: e.detail }));
    };
    const handleProfileUpdate = (e: any) => {
      if(e.detail?.name) setProfile((prev: any) => ({ ...prev, name: e.detail.name }));
    };

    window.addEventListener('avatarUpdated', handleAvatarUpdate);
    window.addEventListener('profileUpdated', handleProfileUpdate);
    return () => {
        window.removeEventListener('avatarUpdated', handleAvatarUpdate);
        window.removeEventListener('profileUpdated', handleProfileUpdate);
    };
  }, []);

  const [isOpen, setIsOpen] = useState(false);
  const [isThemeDark, setIsThemeDark] = useState(true);
  

  const [activeItem, setActiveItem] = useState("dashboard");

  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (pathname?.includes("/panel/instances")) {
        setActiveItem("instances");
    } else if (pathname?.includes("/panel/analytics")) {
        setActiveItem("analytics");
    } else if (pathname?.includes("/panel/documents")) {
        setActiveItem("documents");
    } else if (pathname?.includes("/settings")) {
        setActiveItem("settings");
    } else if (pathname?.includes("/help")) {
        setActiveItem("help");
    } else if (pathname?.includes("/workspace")) {
        setActiveItem("admin-chat");
    } else {
        setActiveItem("dashboard");
    }


    const handleResize = () => {
      if (window.innerWidth >= 768) {
        setIsOpen(true);
      } else {
        setIsOpen(false);
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const toggleSidebar = () => setIsOpen(!isOpen);

  
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

  const handleItemClick = (itemId: string, href: string) => {
    if(itemId === "logout") {
        window.location.href = '/dev-portal/login/';
        return;
    }

    if (href) {
        router.push(href);
        setActiveItem(itemId);
        if (window.innerWidth < 768) {
            setIsOpen(false);
        }
        return;
    }

    setActiveItem(itemId);
    if (window.innerWidth < 768) {
      setIsOpen(false);
    }
  };

  return (
    <>
      <button
        onClick={toggleSidebar}
        className="fixed top-4 left-4 z-50 p-2 rounded-md bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 md:hidden hover:bg-neutral-200 dark:hover:bg-neutral-200 dark:bg-neutral-800 transition-all duration-200"
      >
        {isOpen ? <X className="h-5 w-5 text-neutral-700 dark:text-neutral-300" /> : <Menu className="h-5 w-5 text-neutral-700 dark:text-neutral-300" />}
      </button>

      {isOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-30 md:hidden transition-opacity" onClick={toggleSidebar} />
      )}

      
      

      <motion.aside
        animate={{ width: isCollapsed ? 70 : sidebarWidth }}
        transition={isDragging ? { duration: 0 } : { type: "spring", damping: 25, stiffness: 200 }}
        className={`
          bg-neutral-50 dark:bg-[#111111] border-r border-neutral-200 dark:border-neutral-800 z-40 flex flex-col
          ${isOpen ? "fixed inset-y-0 left-0 translate-x-0" : "max-md:fixed max-md:inset-y-0 max-md:left-0 max-md:-translate-x-full"}
          md:translate-x-0
          ${className}
        `}
        style={{ height: "100%", overflowY: "hidden", position: "relative" }}
      >
        {/* Header with logo */}
        <div 
        className={`flex items-center ${isCollapsed ? "flex-col py-5" : "justify-between p-5"} border-b border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-[#111111]/60`}
      >
        {!isCollapsed && (
          <div className="flex items-center space-x-3 w-full">
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
            <div className="h-8 rounded-lg flex items-center justify-center hover:scale-105 cursor-pointer transition-transform mb-4" title="Expand Sidebar" onClick={(e) => { e.stopPropagation(); setIsCollapsed(false); }}>
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
          {/* Navigation */}
          <nav className={`flex-1 ${isCollapsed ? "px-1" : "px-3"} py-4 overflow-y-auto custom-scrollbar`}>
            <ul className="space-y-1">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                const isActive = activeItem === item.id;

                return (
                  <li key={item.id}>
                    <button
                      onClick={() => handleItemClick(item.id, item.href)}
                      className={`
                        w-full flex items-center py-2 text-left transition-all duration-150 group border-l-2
                        ${isCollapsed ? "justify-center rounded-md px-0" : "space-x-3 rounded-r-md pl-[10px] pr-3"}
                        ${isActive
                          ? "border-[#e05a2b] text-[#e05a2b] bg-transparent"
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
                          {item.badge && (
                            <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${isActive ? "bg-[#e05a2b]/10 text-[#e05a2b]" : "bg-neutral-200 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400"}`}>
                              {item.badge}
                            </span>
                          )}
                        </div>
                      )}
                    </button>
                  </li>
                );
              })}
            </ul>
            
            {/* Chats List */}
            <div className={`mt-6 mb-2 flex items-center justify-between ${isCollapsed ? "px-1 justify-center" : "px-4"}`}>
              {!isCollapsed && <span className="text-xs font-semibold text-neutral-500 uppercase tracking-wider">Chats</span>}
              <button className={`p-1 hover:bg-neutral-200 dark:hover:bg-neutral-800 rounded-md text-neutral-500 transition-colors ${isCollapsed ? "mx-auto" : ""}`}>
                <Plus className="w-4 h-4" />
              </button>
            </div>
            {!isCollapsed && (
              <div className="px-4 mb-3 relative">
                <Search className="absolute left-6 top-1.5 h-3.5 w-3.5 text-neutral-400" />
                <input 
                  type="text"
                  placeholder="Search chats..." 
                  className="w-full pl-8 h-7 bg-neutral-200 dark:bg-[#1a1a1a] border border-transparent focus:border-neutral-300 dark:focus:border-neutral-700 rounded-md text-xs text-neutral-800 dark:text-neutral-200 focus:outline-none transition-colors placeholder:text-neutral-500" 
                />
              </div>
            )}
            <ul className="space-y-0.5 mt-1">
              {recentChats.map((chat, i) => (
                <li key={i}>
                  <button
                    onClick={() => onSelectChat && onSelectChat(chat.chat_id)}
                    className={`
                      w-full flex items-center py-2 text-left transition-all duration-150 group
                      ${isCollapsed ? "justify-center rounded-md px-0 mx-1" : "space-x-3 rounded-r-md pl-4 pr-3"}
                      hover:bg-neutral-100 dark:hover:bg-white/5 text-neutral-600 dark:text-[#888]
                    `}
                    title={isCollapsed ? chat.title : undefined}
                  >
                    {isCollapsed ? (
                      <div className="flex items-center justify-center min-w-[24px]">
                        <MessageSquare className="h-4 w-4 flex-shrink-0 text-neutral-400" />
                      </div>
                    ) : (
                      <div className="flex flex-col w-full overflow-hidden">
                        <span className="text-sm font-medium truncate group-hover:text-neutral-900 dark:group-hover:text-neutral-200 transition-colors">{chat.title}</span>
                        <span className="text-[10px] text-neutral-400">{chat.date}</span>
                      </div>
                    )}
                  </button>
                </li>
              ))}
            </ul>

          </nav>

          {/* Bottom section */}
          <div className={`mt-auto pb-6 flex flex-col pt-4 border-t border-neutral-200 dark:border-neutral-800/50 ${isCollapsed ? "gap-4 items-center px-1" : "gap-5 px-4"}`}>
            {/* Profile Area */}
            <div 
              onClick={() => handleItemClick('settings', '/settings/')}
              className={`flex items-center cursor-pointer group ${isCollapsed ? "justify-center" : "justify-start"}`}
              title="Settings & Profile"
            >
              <div className="h-9 w-9 rounded-full overflow-hidden flex items-center justify-center flex-shrink-0 shadow-sm">
                  {profile.avatar ? <img src={profile.avatar} className="w-full h-full object-cover" /> : <span className="font-bold text-neutral-600 dark:text-[#ccc] text-sm">{profile.name?.charAt(0)}</span>}
              </div>
              
              {!isCollapsed && (
                <div className="ml-3 flex flex-col min-w-0">
                  <span className={`text-sm font-semibold truncate transition-colors ${activeItem === 'settings' ? 'text-[#e05a2b]' : 'text-neutral-900 dark:text-white group-hover:text-[#e05a2b]'}`}>{profile.name}</span>
                  <span className="text-xs text-neutral-500 dark:text-neutral-400 truncate">{profile.email}</span>
                </div>
              )}
            </div>

            {isDev && (
              <div
                onClick={() => handleItemClick('panel', '/panel/')}
                className={`flex items-center cursor-pointer group transition-colors ${isCollapsed ? "justify-center" : "justify-start"} ${activeItem === 'help' ? 'text-[#e05a2b]' : 'text-neutral-500 hover:text-neutral-900 dark:hover:text-white'}`}
                title={isCollapsed ? "Back to Panel" : undefined}
              >
                <ChevronLeft className="h-4 w-4 flex-shrink-0" />
                {!isCollapsed && <span className="ml-3 text-xs font-medium">Back to Panel</span>}
              </div>
            )}
            

          </div>
        </div>
        {children}

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
