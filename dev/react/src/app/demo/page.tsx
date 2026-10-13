"use client";
import { useState, useEffect } from "react";
import { AnimatedAIChat } from "@/components/ui/animated-ai-chat"
import { DemoSidebar } from "@/components/ui/demo-side-bar"
import { Topbar } from "@/components/ui/topbar";

import { useTheme } from "@/components/theme-provider";

export default function DemoPage() {
  const { isDark, toggleDark } = useTheme();
  const setIsDark = (val: boolean | ((prev: boolean) => boolean)) => {
    const nextVal = typeof val === 'function' ? val(isDark) : val;
    if (nextVal !== isDark) {
      toggleDark();
    }
  };

  return (
    <div className="flex w-screen h-screen bg-[#fafafa] dark:bg-black overflow-hidden relative">
      <DemoSidebar />
      <div className="flex flex-col flex-1 h-full relative">
        <div className="absolute top-0 w-full z-10 px-6 pt-6 pointer-events-none">
            <div className="pointer-events-auto">
                <Topbar title="" subtitle="" isDark={isDark} setIsDark={setIsDark} />
            </div>
        </div>
        <AnimatedAIChat />
      </div>
    </div>
  );
}
