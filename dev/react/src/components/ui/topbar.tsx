"use client";

import { Bell, Search, Menu, Sun, Moon, Calendar, CheckCircle2 } from "lucide-react";
import * as Popover from "@radix-ui/react-popover";
import { useState, useContext } from "react";
import { ThemeContext } from "@/components/theme-provider";
import { playSound } from "@/lib/sound";

export function Topbar({ title, subtitle, children }: any) {
  const { isDark, toggleDark } = useContext(ThemeContext);

  const [notifications, setNotifications] = useState([
      { id: 1, type: "alert", text: "High latency detected on instance-x", time: "2 mins ago", read: false },
      { id: 2, type: "warning", text: "API key nearing usage limit", time: "1 hour ago", read: false },
      { id: 3, type: "success", text: "Backup completed successfully", time: "3 hours ago", read: true },
  ]);

  const unreadCount = notifications.filter(n => !n.read).length;

  const markRead = (id: number) => {
      setNotifications(notifications.map(n => n.id === id ? { ...n, read: true } : n));
  };

  const markAllRead = () => {
      setNotifications(notifications.map(n => ({ ...n, read: true })));
  };

  return (
    <div className="w-full flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-transparent mb-8">
      <div className="flex items-start sm:items-center gap-4">
        <button 
            className="md:hidden mt-1 sm:mt-0 flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-neutral-200 dark:border-[#333] bg-white dark:bg-[#2e2e2e] text-neutral-600 dark:text-[#888888] hover:bg-neutral-100 dark:hover:bg-[#383838] transition-all"
        >
            <Menu className="h-4 w-4" />
        </button>
        {title && (
            <div className="space-y-1">
                <h1 className="text-3xl sm:text-4xl lg:text-[40px] font-bold text-neutral-900 dark:text-white tracking-tight leading-tight">{title}</h1>
                {subtitle && (
                  <p className="text-sm sm:text-base text-neutral-500 dark:text-neutral-400 font-medium">{subtitle}</p>
                )}
            </div>
        )}
      </div>

      <div className="flex items-center gap-3 self-end sm:self-center shrink-0">
        {children}

        {/* Theme Toggle */}
        <button 
          onClick={toggleDark}
          className="flex h-9 w-9 items-center justify-center rounded-full border border-neutral-200 dark:border-[#333] bg-white dark:bg-[#2e2e2e] text-neutral-600 dark:text-[#888888] hover:bg-neutral-100 dark:hover:bg-[#383838] transition-all"
        >
          {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </button>

        {/* Notifications */}
        <Popover.Root>
            <Popover.Trigger asChild>
                <button 
                  onClick={() => playSound("perk")}
                  className="relative flex h-9 w-9 items-center justify-center rounded-full border border-neutral-200 dark:border-[#333] bg-white dark:bg-[#2e2e2e] text-neutral-600 dark:text-[#888888] hover:bg-neutral-100 dark:hover:bg-[#383838] transition-all"
                >
                    <Bell className="h-4 w-4" />
                    {unreadCount > 0 && <span className="absolute top-2 right-2 h-2 w-2 bg-[#e05a2b] rounded-full"></span>}
                </button>
            </Popover.Trigger>
            <Popover.Portal>
                <Popover.Content className="z-50 w-80 bg-white dark:bg-[#1e1e1e] border border-neutral-200 dark:border-[#2a2a2a] rounded-[12px] shadow-lg overflow-hidden flex flex-col" sideOffset={8} align="end">
                    <div className="flex items-center justify-between p-4 border-b border-neutral-100 dark:border-[#2a2a2a]/50">
                        <span className="font-semibold text-sm text-neutral-900 dark:text-white">Notifications</span>
                        {unreadCount > 0 && (
                            <button onClick={markAllRead} className="text-[12px] font-medium text-[#e05a2b] hover:underline">
                                Mark all as read
                            </button>
                        )}
                    </div>
                    <div className="max-h-80 overflow-y-auto">
                        {notifications.length === 0 ? (
                            <div className="p-8 text-center text-[#555] text-sm">No notifications yet</div>
                        ) : (
                            <div className="flex flex-col">
                                {notifications.map((notif: any) => (
                                    <div 
                                        key={notif.id} 
                                        onClick={() => markRead(notif.id)}
                                        className={`flex gap-3 p-4 cursor-pointer transition-colors border-b border-neutral-100 dark:border-[#2a2a2a]/50 last:border-0 ${notif.read ? 'bg-transparent hover:bg-neutral-50 dark:hover:bg-[#2a2a2a]' : 'bg-neutral-50 dark:bg-[#252525] hover:bg-neutral-100 dark:hover:bg-[#2a2a2a]'}`}
                                    >
                                        <div className="mt-1">
                                            <span className={`block w-2 h-2 rounded-full ${notif.type === 'alert' ? 'bg-[#e05a2b]' : notif.type === 'warning' ? 'bg-orange-500' : 'bg-emerald-500'}`}></span>
                                        </div>
                                        <div className="flex-1">
                                            <p className="text-[13px] text-neutral-800 dark:text-[#ccc]">{notif.text}</p>
                                            <p className="text-[11px] text-neutral-500 dark:text-[#555] mt-1">{notif.time}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </Popover.Content>
            </Popover.Portal>
        </Popover.Root>
      </div>
    </div>
  );
}
