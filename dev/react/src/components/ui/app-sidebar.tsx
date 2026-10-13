"use client";

import { useState, useEffect } from "react";
import { Bell, HelpCircle, Settings, Shield, User, ChevronsUpDown, Calendar, Inbox, Bot, Plus, Search, LayoutDashboard, Home as HomeIcon, TerminalSquare, Key, LogOut, Users, BookOpen, Target } from "lucide-react"
import { 
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarFooter,
} from "@/components/ui/sidebar"
import { Input } from "@/components/ui/input"
import { UserProfileSidebar } from "@/components/ui/menu"

const items = [
  { title: "Menú", url: "/panel/", icon: HomeIcon },
  { title: "IA Config", url: "/", icon: Bot },
  { title: "Seguridad", url: "#", icon: Shield },
  { title: "API Keys", url: "#", icon: Key },
  { title: "Logs", url: "#", icon: TerminalSquare },
]

export function AppSidebar({ onSelectChat }: { onSelectChat?: (chatId: string) => void }) {
  const [profile, setProfile] = useState<any>({ name: "Santiago", email: "Santi21435@gmail.com", avatar: "https://images.unsplash.com/photo-1531427186611-ecfd6d936c79?w=900&auto=format&fit=crop&q=60" });

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem("dev_master_key") || "";
        const res = await fetch("/api/user/profile", { headers: { "x-master-key": token } });
        if (res.ok) {
          const data = await res.json();
          setProfile((prev: any) => ({ ...prev, name: data.name, email: data.email, avatar: data.avatar }));
        }
      } catch (e) {}
    };
    fetchProfile();

    const handleAvatarUpdate = (e: any) => setProfile((prev: any) => ({ ...prev, avatar: e.detail }));
    const handleProfileUpdate = (e: any) => { if(e.detail?.name) setProfile((prev: any) => ({ ...prev, name: e.detail.name })); };
    window.addEventListener('avatarUpdated', handleAvatarUpdate);
    window.addEventListener('profileUpdated', handleProfileUpdate);
    return () => {
        window.removeEventListener('avatarUpdated', handleAvatarUpdate);
        window.removeEventListener('profileUpdated', handleProfileUpdate);
    };
  }, []);

  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [recentChats, setRecentChats] = useState<{title: string, date: string, chat_id: string}[]>([]);

  useEffect(() => {
    fetch('/api/dev/chats')
      .then(res => res.json())
      .then(data => {
        if (data.conversations && data.conversations.length > 0) {
          setRecentChats(data.conversations);
        } else {
            setRecentChats([]);
        }
      })
      .catch(() => setRecentChats([]));
  }, []);

  return (
    <Sidebar variant="sidebar" className="dark bg-neutral-950 border-r border-neutral-900">
      <SidebarContent className="custom-scrollbar">
        <SidebarGroup>
          <SidebarGroupLabel className="text-neutral-400">Application</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild tooltip={item.title} className="hover:bg-neutral-900 text-neutral-300">
                    <button onClick={() => { window.location.href = `/dev-portal${item.url}`; }} className="w-full flex items-center justify-start text-left">
                      <item.icon className="text-neutral-400 mr-2" />
                      <span>{item.title}</span>
                    </button>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <div className="px-4 py-2 mt-2">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-neutral-400">Chats</span>
            <button className="p-1 hover:bg-neutral-800 rounded-md text-neutral-400 transition-colors">
              <Plus className="w-4 h-4" />
            </button>
          </div>
          <div className="relative mb-4">
            <Search className="absolute left-2.5 top-2 h-4 w-4 text-neutral-500" />
            <Input 
              placeholder="Search chats..." 
              className="pl-8 h-8 bg-neutral-900 border-neutral-800 text-xs focus-visible:ring-1 focus-visible:ring-neutral-700 placeholder:text-neutral-500" 
            />
          </div>
        </div>

        <SidebarGroup className="pt-0 flex-1 overflow-hidden flex flex-col">
          <SidebarGroupContent className="flex-1 overflow-y-auto custom-scrollbar">
            <SidebarMenu className="gap-0.5">
              {recentChats.map((chat, i) => (
                <SidebarMenuItem key={i}>
                  <SidebarMenuButton asChild className="hover:bg-neutral-900 text-neutral-300 h-auto py-2 items-start group">
                    <button onClick={() => onSelectChat && onSelectChat(chat.chat_id)} className="flex flex-col gap-1 w-full overflow-hidden text-left cursor-pointer">
                      <span className="text-sm font-normal truncate w-full group-hover:text-neutral-50 transition-colors">
                        {chat.title}
                      </span>
                      <span className="text-[10px] text-neutral-500">
                        {chat.date}
                      </span>
                    </button>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="relative">
        {showProfileMenu && (
            <div className="absolute bottom-full left-4 mb-2 z-50">
                <UserProfileSidebar 
                    user={{ name: profile.name, email: profile.email, avatarUrl: profile.avatar }}
                    navItems={[
                        { label: 'Main Dashboard', href: '/panel', icon: <LayoutDashboard /> },
                        { label: 'Clients', href: '/clients', icon: <Users /> },
                        { label: 'Training', href: '/training', icon: <BookOpen /> },
                        { label: 'Goals', href: '/goals', icon: <Target />, isSeparator: true },
                    ]}
                    logoutItem={{
                        label: 'Log out', icon: <LogOut />, onClick: () => { window.location.href = '/api/auth/sign-in'; }
                    }}
                />
            </div>
        )}
        <SidebarGroup>
          <SidebarMenuButton onClick={() => setShowProfileMenu(!showProfileMenu)} className="w-full justify-between gap-3 h-12 hover:bg-neutral-900 text-neutral-300">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-neutral-800 flex items-center justify-center overflow-hidden">
                {profile.avatar ? <img src={profile.avatar} className="w-full h-full object-cover" alt="User Avatar" /> : <span className="font-bold text-neutral-400 text-sm">{profile.name?.charAt(0)}</span>}
              </div>
              <div className="flex flex-col items-start">
                <span className="text-sm font-medium">{profile.name}</span>
                <span className="text-xs text-neutral-500 truncate w-32">{profile.email}</span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button className="p-1.5 hover:bg-neutral-800 rounded-md text-neutral-400 hover:text-white transition-colors">
                <Settings className="h-4 w-4" />
              </button>
              <ChevronsUpDown className="h-4 w-4 text-neutral-500" />
            </div>
          </SidebarMenuButton>
        </SidebarGroup>
      </SidebarFooter>
    </Sidebar>
  )
}
