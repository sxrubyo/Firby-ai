"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Search, X } from "lucide-react";
import { useState } from "react";

type ExpandingSearchDockProps = {
  onSearch?: (query: string) => void;
  placeholder?: string;
};

export function ExpandingSearchDock({
  onSearch,
  placeholder = "Search...",
}: ExpandingSearchDockProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [query, setQuery] = useState("");

  const handleExpand = () => {
    setIsExpanded(true);
  };

  const handleCollapse = () => {
    setIsExpanded(false);
    setQuery("");
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (onSearch && query) {
      onSearch(query);
    }
  };

  return (
    <div className="relative">
      <AnimatePresence mode="wait">
        {!isExpanded ? (
          <motion.button
            key="icon"
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            onClick={handleExpand}
            className="flex h-9 w-9 items-center justify-center rounded-full border border-neutral-200 dark:border-[#333] bg-white dark:bg-[#2e2e2e] text-neutral-600 dark:text-[#888888] transition-colors hover:bg-neutral-100 dark:hover:bg-[#383838]"
          >
            <Search className="h-4 w-4" />
          </motion.button>
        ) : (
          <motion.form
            key="input"
            initial={{ width: 36, opacity: 0 }}
            animate={{ width: 280, opacity: 1 }}
            exit={{ width: 36, opacity: 0 }}
            transition={{
              type: "spring",
              stiffness: 300,
              damping: 30,
            }}
            onSubmit={handleSubmit}
            className="relative"
          >
            <motion.div
              initial={{ backdropFilter: "blur(0px)" }}
              animate={{ backdropFilter: "blur(12px)" }}
              className="relative flex items-center gap-2 overflow-hidden rounded-full border border-neutral-200 dark:border-[#333] bg-white/80 dark:bg-[#2e2e2e]/80 backdrop-blur-md h-9"
            >
              <div className="ml-3">
                <Search className="h-4 w-4 text-neutral-500 dark:text-[#888888]" />
              </div>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={placeholder}
                autoFocus
                className="h-full flex-1 bg-transparent pr-2 text-sm outline-none placeholder:text-neutral-500 dark:placeholder:text-[#888888] text-neutral-900 dark:text-white"
              />
              <motion.button
                type="button"
                onClick={handleCollapse}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                className="mr-1 flex h-7 w-7 items-center justify-center rounded-full hover:bg-neutral-100 dark:hover:bg-[#383838] text-neutral-500 dark:text-[#888888]"
              >
                <X className="h-3 w-3" />
              </motion.button>
            </motion.div>
          </motion.form>
        )}
      </AnimatePresence>
    </div>
  );
}
