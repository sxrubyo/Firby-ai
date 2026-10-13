"use client";
import { MessageLoading } from "@/components/ui/message-loading";
import { ShiningText } from "@/components/ui/shining-text";

import { useEffect, useRef, useCallback, useTransition } from "react";
import { useState } from "react";
import { cn } from "@/lib/utils";
import {
    ImageIcon,
    FileUp,
    Layout,
    MonitorIcon,
    CircleUserRound,
    ArrowUpIcon,
    Paperclip,
    PlusIcon,
    SendIcon,
    XIcon,
    LoaderIcon,
    Sparkles,
    Command,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import * as React from "react"

interface UseAutoResizeTextareaProps {
    minHeight: number;
    maxHeight?: number;
}

function useAutoResizeTextarea({
    minHeight,
    maxHeight,
}: UseAutoResizeTextareaProps) {
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const adjustHeight = useCallback(
        (reset?: boolean) => {
            const textarea = textareaRef.current;
            if (!textarea) return;

            if (reset) {
                textarea.style.height = `${minHeight}px`;
                return;
            }

            textarea.style.height = `${minHeight}px`;
            const newHeight = Math.max(
                minHeight,
                Math.min(
                    textarea.scrollHeight,
                    maxHeight ?? Number.POSITIVE_INFINITY
                )
            );

            textarea.style.height = `${newHeight}px`;
        },
        [minHeight, maxHeight]
    );

    useEffect(() => {
        const textarea = textareaRef.current;
        if (textarea) {
            textarea.style.height = `${minHeight}px`;
        }
    }, [minHeight]);

    useEffect(() => {
        const handleResize = () => adjustHeight();
        window.addEventListener("resize", handleResize);
        return () => window.removeEventListener("resize", handleResize);
    }, [adjustHeight]);

    return { textareaRef, adjustHeight };
}

interface CommandSuggestion {
    icon: React.ReactNode;
    label: string;
    description: string;
    prefix: string;
}

interface ChatMessage {
    id: string;
    role: "user" | "assistant";
    content: string;
}

interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  containerClassName?: string;
  showRing?: boolean;
}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, containerClassName, showRing = true, ...props }, ref) => {
    const [isFocused, setIsFocused] = React.useState(false);
    
    return (
      <div className={cn(
        "relative",
        containerClassName
      )}>
        <textarea
          className={cn(
            "flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm",
            "transition-all duration-200 ease-in-out",
            "placeholder:text-muted-foreground",
            "disabled:cursor-not-allowed disabled:opacity-50",
            showRing ? "focus-visible:outline-none focus-visible:ring-0 focus-visible:ring-offset-0" : "",
            className
          )}
          ref={ref}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          {...props}
        />
        
        {showRing && isFocused && (
          <motion.span 
            className="absolute inset-0 rounded-md pointer-events-none ring-2 ring-offset-0 ring-violet-500/30"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          />
        )}

        {props.onChange && (
          <div 
            className="absolute bottom-2 right-2 opacity-0 w-2 h-2 bg-violet-500 rounded-full"
            style={{
              animation: 'none',
            }}
            id="textarea-ripple"
          />
        )}
      </div>
    )
  }
)
Textarea.displayName = "Textarea"

export function AnimatedAIChat() {
    const [value, setValue] = useState("");
    const [attachments, setAttachments] = useState<string[]>([]);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [isTyping, setIsTyping] = useState(false);
    const [activeSuggestion, setActiveSuggestion] = useState<number>(-1);
    const [showCommandPalette, setShowCommandPalette] = useState(false);
    const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
    const { textareaRef, adjustHeight } = useAutoResizeTextarea({
        minHeight: 60,
        maxHeight: 200,
    });
    const [inputFocused, setInputFocused] = useState(false);
    const commandPaletteRef = useRef<HTMLDivElement>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const commandSuggestions: CommandSuggestion[] = [
        { 
            icon: <ImageIcon className="w-4 h-4" />, 
            label: "Clone UI", 
            description: "Generate a UI from a screenshot", 
            prefix: "/clone" 
        },
        { 
            icon: <Layout className="w-4 h-4" />, 
            label: "Import Figma", 
            description: "Import a design from Figma", 
            prefix: "/figma" 
        },
        { 
            icon: <MonitorIcon className="w-4 h-4" />, 
            label: "Create Page", 
            description: "Generate a new web page", 
            prefix: "/page" 
        },
        { 
            icon: <Sparkles className="w-4 h-4" />, 
            label: "Improve", 
            description: "Improve existing UI design", 
            prefix: "/improve" 
        },
    ];

    useEffect(() => {
        if (value.startsWith('/') && !value.includes(' ')) {
            setShowCommandPalette(true);
            const matchingSuggestionIndex = commandSuggestions.findIndex(
                (cmd) => cmd.prefix.startsWith(value)
            );
            setActiveSuggestion(matchingSuggestionIndex >= 0 ? matchingSuggestionIndex : -1);
        } else {
            setShowCommandPalette(false);
        }
    }, [value]);

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            setMousePosition({ x: e.clientX, y: e.clientY });
        };
        window.addEventListener('mousemove', handleMouseMove);
        return () => window.removeEventListener('mousemove', handleMouseMove);
    }, []);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, isTyping]);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            const target = event.target as Node;
            if (commandPaletteRef.current && !commandPaletteRef.current.contains(target)) {
                setShowCommandPalette(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (showCommandPalette) {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                setActiveSuggestion(prev => prev < commandSuggestions.length - 1 ? prev + 1 : 0);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                setActiveSuggestion(prev => prev > 0 ? prev - 1 : commandSuggestions.length - 1);
            } else if (e.key === 'Tab' || e.key === 'Enter') {
                e.preventDefault();
                if (activeSuggestion >= 0) {
                    const selectedCommand = commandSuggestions[activeSuggestion];
                    setValue(selectedCommand.prefix + ' ');
                    setShowCommandPalette(false);
                }
            } else if (e.key === 'Escape') {
                e.preventDefault();
                setShowCommandPalette(false);
            }
        } else if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            if (value.trim()) handleSendMessage();
        }
    };

    const handleSendMessage = async () => {
        const messageText = value.trim();
        if (!messageText || isTyping) return;

        const userId = (() => {
            if (typeof window === "undefined") return "web_demo";
            const existing = localStorage.getItem("firby_demo_user_id");
            if (existing) return existing;
            const generated = `web_demo_${window.crypto?.randomUUID?.() || Date.now().toString(36)}`;
            localStorage.setItem("firby_demo_user_id", generated);
            return generated;
        })();

        const token = localStorage.getItem("firby_master_key") || localStorage.getItem("dev_master_key") || "";
        const attachmentLine = attachments.length ? `\nAdjuntos: ${attachments.join(", ")}` : "";

        setMessages((prev) => [...prev, { id: `${Date.now()}-user`, role: "user", content: messageText }]);
        setValue("");
        adjustHeight(true);
        setIsTyping(true);

        try {
            const res = await fetch("/test", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    ...(token ? { "X-Master-Key": token } : {}),
                },
                body: JSON.stringify({
                    message: `${messageText}${attachmentLine}`,
                    user_id: userId,
                }),
            });

            const data = await res.json().catch(() => ({}));
            if (!res.ok) throw new Error(data.detail || "No fue posible conectar con Firby");

            const bubbles = Array.isArray(data.bubbles) && data.bubbles.length > 0
                ? data.bubbles
                : [data.response || "(sin respuesta)"];

            const assistantMessages: ChatMessage[] = bubbles
                .map((bubble: any, index: number) => ({
                    id: `${Date.now()}-assistant-${index}`,
                    role: "assistant" as const,
                    content: typeof bubble === "string" ? bubble : bubble?.content || bubble?.text || JSON.stringify(bubble),
                }))
                .filter((bubble: ChatMessage) => bubble.content && bubble.content.trim());

            setMessages((prev) => [...prev, ...assistantMessages]);
        } catch (err: any) {
            setMessages((prev) => [...prev, { id: `${Date.now()}-error`, role: "assistant", content: `Error: ${err?.message || "No response"}` }]);
        } finally {
            setIsTyping(false);
        }
    };

    const handleAttachFile = () => {
        const mockFileName = `file-${Math.floor(Math.random() * 1000)}.pdf`;
        setAttachments(prev => [...prev, mockFileName]);
    };

    const removeAttachment = (index: number) => {
        setAttachments(prev => prev.filter((_, i) => i !== index));
    };

    const selectCommandSuggestion = (index: number) => {
        const selectedCommand = commandSuggestions[index];
        const text = selectedCommand.prefix;
        setValue(text);
        setShowCommandPalette(false);
        // Add a slight delay to allow React state to update the value before sending
        setTimeout(() => {
            if (textareaRef.current) {
                textareaRef.current.focus();
            }
        }, 50);
    };

    return (
        <div className="h-full w-full flex flex-col bg-transparent text-neutral-900 dark:text-white relative overflow-hidden">
            {/* Background Effects */}
            <div className="absolute inset-0 w-full h-full overflow-hidden pointer-events-none">
                <div className="absolute top-0 left-1/4 w-96 h-96 bg-violet-500/5 rounded-full filter blur-[128px]" />
                <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-indigo-500/5 rounded-full filter blur-[128px]" />
            </div>

            {/* Main Content Area */}
            <div className={cn(
                "flex-1 flex flex-col relative z-10",
                messages.length === 0 ? "justify-center items-center" : "overflow-hidden"
            )}>
                
                {/* 1. WELCOME SCREEN (Only when empty) */}
                <AnimatePresence>
                    {messages.length === 0 && (
                        <motion.div
                            key="welcome-header"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            transition={{ duration: 0.4 }}
                            className="w-full max-w-2xl mx-auto text-center space-y-6 mb-10 px-4"
                        >
                            <h1 className="text-4xl font-semibold tracking-tight text-neutral-900 dark:text-white">
                                How can I help today?
                            </h1>
                            <p className="text-neutral-500 dark:text-neutral-400">
                                Start a conversation with Firby to build, design, or explore.
                            </p>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* 2. MESSAGES LIST (Only when chatting) */}
                {messages.length > 0 && (
                    <div className="flex-1 overflow-y-auto px-4 py-8 custom-scrollbar">
                        <div className="w-full max-w-3xl mx-auto space-y-10 pb-20">
                            {messages.map((message) => (
                                <motion.div
                                    key={message.id}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className={cn(
                                        "flex w-full gap-5",
                                        message.role === "user" ? "justify-end" : "justify-start"
                                    )}
                                >
                                    {message.role === "assistant" && (
                                        <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                                            <img src="/favicon.png" alt="Firby" className="w-6 h-6 object-contain brightness-0 invert" />
                                        </div>
                                    )}
                                    <div className={cn(
                                        "max-w-[85%] text-base leading-7",
                                        message.role === "user" 
                                            ? "bg-neutral-100 dark:bg-white/10 px-4 py-2.5 rounded-2xl text-neutral-900 dark:text-white border border-neutral-200 dark:border-white/5" 
                                            : "text-neutral-800 dark:text-neutral-100 py-1"
                                    )}
                                        dangerouslySetInnerHTML={{ __html: message.content.replace(/\n/g, '<br/>') }}
                                    />
                                </motion.div>
                            ))}
                            
                            {isTyping && (
                                <motion.div 
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="flex items-center gap-5"
                                >
                                    <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0">
                                        <img src="/favicon.png" alt="Firby" className="w-6 h-6 object-contain brightness-0 invert" />
                                    </div>
                                    <div className="flex items-center gap-3 text-neutral-400">
                                        <MessageLoading />
                                        <ShiningText text="Firby is thinking..." />
                                    </div>
                                </motion.div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>
                    </div>
                )}

                
                {/* 2.5 VERTICAL SUGGESTIONS ON THE LEFT (Only when chatting) */}
                <AnimatePresence>
                    {messages.length > 0 && (
                        <motion.div 
                            className="absolute left-6 top-1/2 -translate-y-1/2 flex flex-col gap-3 z-20 hidden md:flex"
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            transition={{ delay: 0.2 }}
                        >
                            {commandSuggestions.map((suggestion, index) => (
                                <motion.button
                                    key={suggestion.prefix + "-vert"}
                                    onClick={() => selectCommandSuggestion(index)}
                                    className="flex items-center justify-center w-12 h-12 bg-white dark:bg-white/5 hover:bg-neutral-100 dark:hover:bg-white/10 rounded-2xl text-sm transition-all border border-neutral-200 dark:border-white/10 shadow-sm text-neutral-500 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white group relative"
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                >
                                    {suggestion.icon}
                                    <div className="absolute left-full ml-3 px-2 py-1 bg-neutral-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap">
                                        {suggestion.label}
                                    </div>
                                </motion.button>
                            ))}
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* 3. INPUT BAR & SUGGESTIONS CONTAINER */}
                <motion.div 
                    layout
                    className={cn(
                        "w-full max-w-3xl mx-auto p-4 relative z-20 transition-all duration-500",
                        messages.length === 0 ? "mb-0" : "pb-8"
                    )}
                >
                    {/* Input Container */}
                    <motion.div 
                        layout
                        className="relative backdrop-blur-2xl bg-white/70 dark:bg-neutral-900/70 rounded-3xl border border-neutral-200 dark:border-white/10 shadow-xl overflow-hidden"
                    >
                        <AnimatePresence>
                            {showCommandPalette && (
                                <motion.div 
                                    ref={commandPaletteRef}
                                    className="absolute bottom-full left-0 w-full mb-2 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-white/10 rounded-2xl shadow-2xl overflow-hidden"
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: 10 }}
                                >
                                    <div className="py-2">
                                        {commandSuggestions.map((suggestion, index) => (
                                            <button
                                                key={suggestion.prefix}
                                                onClick={() => selectCommandSuggestion(index)}
                                                className={cn(
                                                    "w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-colors",
                                                    activeSuggestion === index ? "bg-violet-500/10 text-violet-500" : "hover:bg-neutral-100 dark:hover:bg-white/5"
                                                )}
                                            >
                                                {suggestion.icon}
                                                <span className="font-medium">{suggestion.label}</span>
                                                <span className="text-neutral-400 text-xs ml-auto">{suggestion.prefix}</span>
                                            </button>
                                        ))}
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <div className="p-3">
                            <Textarea
                                ref={textareaRef}
                                value={value}
                                onChange={(e) => {
                                    setValue(e.target.value);
                                    adjustHeight();
                                }}
                                onKeyDown={handleKeyDown}
                                onFocus={() => setInputFocused(true)}
                                onBlur={() => setInputFocused(false)}
                                placeholder="Ask Firby anything..."
                                className="bg-transparent border-none focus:ring-0 min-h-[60px] max-h-[200px] py-3 px-4 resize-none text-base"
                                showRing={false}
                            />
                            
                            <AnimatePresence>
                                {attachments.length > 0 && (
                                    <motion.div 
                                        className="flex flex-wrap gap-2 px-4 pb-2"
                                        initial={{ opacity: 0, height: 0 }}
                                        animate={{ opacity: 1, height: "auto" }}
                                        exit={{ opacity: 0, height: 0 }}
                                    >
                                        {attachments.map((file, idx) => (
                                            <div key={idx} className="flex items-center gap-2 bg-neutral-100 dark:bg-white/5 px-2.5 py-1.5 rounded-lg text-xs border border-neutral-200 dark:border-white/5">
                                                <span className="truncate max-w-[120px]">{file}</span>
                                                <button onClick={() => removeAttachment(idx)} className="hover:text-red-500 transition-colors">
                                                    <XIcon className="w-3.5 h-3.5" />
                                                </button>
                                            </div>
                                        ))}
                                    </motion.div>
                                )}
                            </AnimatePresence>

                            <div className="flex items-center justify-between px-2 pb-2 pt-1 border-t border-neutral-100 dark:border-white/5">
                                <div className="flex gap-1">
                                    <button 
                                        onClick={handleAttachFile}
                                        className="p-2.5 text-neutral-400 hover:text-neutral-900 dark:hover:text-white transition-colors rounded-xl hover:bg-neutral-100 dark:hover:bg-white/5"
                                    >
                                        <Paperclip className="w-4.5 h-4.5" />
                                    </button>
                                    <button 
                                        onClick={() => setShowCommandPalette(!showCommandPalette)}
                                        className="p-2.5 text-neutral-400 hover:text-neutral-900 dark:hover:text-white transition-colors rounded-xl hover:bg-neutral-100 dark:hover:bg-white/5"
                                    >
                                        <Command className="w-4.5 h-4.5" />
                                    </button>
                                </div>
                                
                                <button
                                    onClick={handleSendMessage}
                                    disabled={isTyping || !value.trim()}
                                    className={cn(
                                        "w-10 h-10 flex items-center justify-center rounded-2xl transition-all",
                                        value.trim() 
                                            ? "bg-neutral-900 dark:bg-white text-white dark:text-black shadow-lg" 
                                            : "bg-neutral-100 dark:bg-white/5 text-neutral-300 dark:text-neutral-700"
                                    )}
                                >
                                    <SendIcon className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    </motion.div>

                    {/* Suggestions (Only when empty) */}
                    <AnimatePresence>
                        {messages.length === 0 && (
                            <motion.div 
                                className="flex flex-wrap items-center justify-center gap-3 mt-8"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                transition={{ delay: 0.2 }}
                            >
                                {commandSuggestions.map((suggestion, index) => (
                                    <motion.button
                                        key={suggestion.prefix}
                                        onClick={() => selectCommandSuggestion(index)}
                                        className="flex items-center gap-2.5 px-4 py-2.5 bg-white dark:bg-white/5 hover:bg-neutral-100 dark:hover:bg-white/10 rounded-2xl text-sm font-medium transition-all border border-neutral-200 dark:border-white/10 shadow-sm"
                                        whileHover={{ y: -2 }}
                                        whileTap={{ scale: 0.98 }}
                                    >
                                        <span className="text-neutral-500 dark:text-neutral-400">{suggestion.icon}</span>
                                        <span>{suggestion.label}</span>
                                    </motion.button>
                                ))}
                            </motion.div>
                        )}
                    </AnimatePresence>
                </motion.div>
            </div>
        </div>
    );
}

function TypingDots() {
    return (
        <div className="flex items-center ml-1">
            {[1, 2, 3].map((dot) => (
                <motion.div
                    key={dot}
                    className="w-1.5 h-1.5 bg-neutral-800 dark:bg-white/90 rounded-full mx-0.5"
                    initial={{ opacity: 0.3 }}
                    animate={{ 
                        opacity: [0.3, 0.9, 0.3],
                        scale: [0.85, 1.1, 0.85]
                    }}
                    transition={{
                        duration: 1.2,
                        repeat: Infinity,
                        delay: dot * 0.15,
                        ease: "easeInOut",
                    }}
                    style={{
                        boxShadow: "0 0 4px rgba(0, 0, 0, 0.1)" /* In light mode it might look fine, or we can remove it */
                    }}
                />
            ))}
        </div>
    );
}

interface ActionButtonProps {
    icon: React.ReactNode;
    label: string;
}

function ActionButton({ icon, label }: ActionButtonProps) {
    const [isHovered, setIsHovered] = useState(false);
    
    return (
        <motion.button
            type="button"
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.97 }}
            onHoverStart={() => setIsHovered(true)}
            onHoverEnd={() => setIsHovered(false)}
            className="flex items-center gap-2 px-4 py-2 bg-neutral-900 hover:bg-neutral-800 rounded-full border border-neutral-800 text-neutral-400 hover:text-neutral-900 dark:text-white transition-all relative overflow-hidden group"
        >
            <div className="relative z-10 flex items-center gap-2">
                {icon}
                <span className="text-xs relative z-10">{label}</span>
            </div>
            
            <AnimatePresence>
                {isHovered && (
                    <motion.div 
                        className="absolute inset-0 bg-gradient-to-r from-violet-500/10 to-indigo-500/10"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.2 }}
                    />
                )}
            </AnimatePresence>
            
            <motion.span 
                className="absolute bottom-0 left-0 w-full h-0.5 bg-gradient-to-r from-violet-500 to-indigo-500"
                initial={{ width: 0 }}
                whileHover={{ width: "100%" }}
                transition={{ duration: 0.3 }}
            />
        </motion.button>
    );
}

const rippleKeyframes = `
@keyframes ripple {
  0% { transform: scale(0.5); opacity: 0.6; }
  100% { transform: scale(2); opacity: 0; }
}
`;

if (typeof document !== 'undefined') {
    const style = document.createElement('style');
    style.innerHTML = rippleKeyframes;
    document.head.appendChild(style);
}
