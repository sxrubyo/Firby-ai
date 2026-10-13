"use client";
import { ThemeContext } from "@/components/theme-provider";
import { useContext } from "react";

import { useState, useEffect } from "react";
import { AnimatedAIChat } from "@/components/ui/animated-ai-chat";
import { ChatSideBar } from "@/components/ui/chat-side-bar";

import { Topbar } from "@/components/ui/topbar";

export default function NewChatsPage() {
  const { isDark, toggleDark } = useContext(ThemeContext);
  
    

  const toggleTheme = toggleDark;

  return (
    
    <div className="flex w-screen h-screen bg-[#fafafa] dark:bg-[#0a0a0b] overflow-hidden relative">
      <ChatSideBar />
      <div className="flex flex-col flex-1 h-full relative">
        <div className="absolute top-0 right-0 w-full z-50 px-6 pt-6 pointer-events-none">
            <div className="pointer-events-auto">
                <Topbar title="" subtitle="" isDark={isDark} setIsDark={toggleTheme} />
            </div>
        </div>
        <AnimatedAIChat />
      </div>
    </div>
    
  );
}
