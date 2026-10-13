"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import {
    ImageIcon,
    PenTool,
    MonitorIcon,
    CircleUserRound,
    ArrowUpIcon,
    Paperclip,
    Bot,
    TerminalSquare,
    Activity,
    Settings,
    RefreshCw,
    Terminal,
    Copy,
    Share
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

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
            const scrollHeight = textarea.scrollHeight;

            if (maxHeight && scrollHeight > maxHeight) {
                textarea.style.height = `${maxHeight}px`;
                textarea.style.overflowY = "auto";
            } else {
                textarea.style.height = `${scrollHeight}px`;
                textarea.style.overflowY = "hidden";
            }
        },
        [minHeight, maxHeight]
    );

    useEffect(() => {
        const textarea = textareaRef.current;
        if (textarea) {
            textarea.addEventListener("input", () => adjustHeight());
        }
        return () => {
            if (textarea) {
                textarea.removeEventListener("input", () => adjustHeight());
            }
        };
    }, [adjustHeight]);

    return { textareaRef, adjustHeight };
}

interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
}

const COMMANDS = [
    { cmd: "/agent", desc: "Cambiar o configurar agente actual", icon: Bot },
    { cmd: "/status", desc: "Ver estado de instancias PM2", icon: Activity },
    { cmd: "/logs", desc: "Ver registros del sistema", icon: TerminalSquare },
    { cmd: "/config", desc: "Abrir configuración ultra", icon: Settings },
    { cmd: "/restart", desc: "Reiniciar instancias o sistema", icon: RefreshCw },
    { cmd: "/cli", desc: "Ejecutar comando directo de firby_cli", icon: Terminal },
];

export function VercelV0Chat({ selectedChatId }: { selectedChatId?: string | null }) {
    const [value, setValue] = useState("");
    const [messages, setMessages] = useState<Message[]>([]);
    const [isTyping, setIsTyping] = useState(false);
    const [showCommands, setShowCommands] = useState(false);
    const [commandFilter, setCommandFilter] = useState("");

    const { textareaRef, adjustHeight } = useAutoResizeTextarea({
        minHeight: 60,
        maxHeight: 200,
    });

    const scrollRef = useRef<HTMLDivElement>(null);

    // Fetch conversation when selectedChatId changes
    useEffect(() => {
        if (!selectedChatId) return;
        
        setIsTyping(true);
        fetch(`/conversations/patient/${selectedChatId}`)
            .then(res => res.json())
            .then(data => {
                if (data.messages) {
                    const loadedMessages: Message[] = data.messages.map((m: any, i: number) => ({
                        id: `hist-${i}`,
                        role: m.role === 'admin' || m.role === 'assistant' ? 'assistant' : 'user',
                        content: m.content || m.text || ''
                    }));
                    setMessages(loadedMessages);
                }
                setIsTyping(false);
            })
            .catch(() => {
                setIsTyping(false);
            });
    }, [selectedChatId]);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, isTyping]);

    const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const val = e.target.value;
        setValue(val);
        adjustHeight();

        if (val.startsWith("/")) {
            setShowCommands(true);
            setCommandFilter(val.toLowerCase());
        } else {
            setShowCommands(false);
        }
    };

    const executeCommand = (cmd: string) => {
        setValue(cmd + " ");
        setShowCommands(false);
        if (textareaRef.current) {
            textareaRef.current.focus();
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            if (showCommands) {
                const visibleCommands = COMMANDS.filter(c => c.cmd.toLowerCase().startsWith(commandFilter));
                if (visibleCommands.length > 0) {
                    executeCommand(visibleCommands[0].cmd);
                    return;
                }
            }
            if (value.trim()) {
                sendMessage(value.trim());
            }
        }
    };

    const sendMessage = async (text: string) => {
        const userMsg: Message = { id: Date.now().toString(), role: "user", content: text };
        setMessages(prev => [...prev, userMsg]);
        setValue("");
        setShowCommands(false);
        adjustHeight(true);
        setIsTyping(true);

        try {
            // Send to DEV API ALWAYS to talk to the Admin Agent.
            const res = await fetch('/api/dev/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, chat_id: selectedChatId })
            });
            const data = await res.json();
            setIsTyping(false);
            setMessages(prev => [...prev, { id: Date.now().toString(), role: "assistant", content: data.reply }]);
            
            if (data.ui_action && data.ui_action.type === 'navigate') {
                setTimeout(() => {
                    window.location.href = data.ui_action.route;
                }, 1500);
            }
        } catch (e) {
            setIsTyping(false);
            setMessages(prev => [...prev, { id: Date.now().toString(), role: "assistant", content: `Error: ${e}` }]);
        }
    };

    const visibleCommands = COMMANDS.filter(c => c.cmd.toLowerCase().startsWith(commandFilter));

    return (
        <div className={cn(
            "flex flex-col items-center w-full max-w-3xl mx-auto px-4 sm:px-6 md:px-8 py-4 flex-1 h-full relative",
            messages.length === 0 ? "justify-center" : "overflow-hidden"
        )}>
            
            {messages.length === 0 && (
                <div className="w-full text-center space-y-8 mb-8">
                    <h1 className="text-4xl font-bold text-black dark:text-white">
                        What can I help you ship?
                    </h1>
                </div>
            )}

            {messages.length > 0 && (
                <div ref={scrollRef} className="w-full flex-1 overflow-y-auto mb-6 pr-2 space-y-6 scroll-smooth custom-scrollbar pb-24 mt-12">
                    {messages.map((msg) => (
                        <motion.div 
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            key={msg.id} 
                            className={cn(
                                "flex w-full group flex-col",
                                msg.role === "user" ? "items-end" : "items-start"
                            )}
                        >
                            <div className={cn(
                                "max-w-[80%] rounded-2xl px-5 py-3 text-sm leading-relaxed whitespace-pre-wrap",
                                msg.role === "user" 
                                    ? "bg-white text-black rounded-br-sm" 
                                    : "bg-neutral-900 border border-neutral-800 text-neutral-100 rounded-bl-sm font-mono"
                            )}>
                                {msg.content}
                            </div>
                            
                            {/* Minimalism transparency actions */}
                            {msg.role === "assistant" && (
                                <div className="flex items-center gap-1 mt-1 opacity-0 group-hover:opacity-100 transition-opacity ml-1">
                                    <button 
                                        onClick={() => navigator.clipboard.writeText(msg.content)}
                                        className="text-neutral-600 hover:text-neutral-300 transition-colors p-1.5 rounded-md"
                                        title="Copiar"
                                    >
                                        <Copy className="w-3.5 h-3.5" />
                                    </button>
                                    <button 
                                        className="text-neutral-600 hover:text-neutral-300 transition-colors p-1.5 rounded-md"
                                        title="Compartir"
                                    >
                                        <Share className="w-3.5 h-3.5" />
                                    </button>
                                </div>
                            )}
                        </motion.div>
                    ))}
                    {isTyping && (
                        <motion.div 
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="flex w-full justify-start"
                        >
                            <div className="max-w-[80%] rounded-2xl px-4 py-3 text-sm bg-neutral-900 border border-neutral-800 text-neutral-100 rounded-bl-sm flex items-center space-x-2">
                                <img 
                                    src="/isotype" 
                                    alt="Thinking" 
                                    className="w-4 h-4 animate-spin opacity-80"
                                    style={{ filter: "brightness(0) invert(1)", background: "transparent", mixBlendMode: "screen" }} 
                                />
                                <span className="text-xs font-medium text-neutral-400">Thinking...</span>
                            </div>
                        </motion.div>
                    )}
                </div>
            )}

            <div className={cn(
                "w-full transition-all duration-500 ease-in-out",
                messages.length > 0 ? "absolute bottom-6 left-1/2 -translate-x-1/2 px-4 sm:px-6 md:px-8 max-w-3xl" : ""
            )}>
                
                <AnimatePresence>
                    {showCommands && visibleCommands.length > 0 && (
                        <motion.div 
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: 10 }}
                            className="absolute bottom-full mb-3 left-4 right-4 bg-neutral-900 border border-neutral-800 rounded-xl overflow-hidden shadow-2xl z-50 max-h-60 overflow-y-auto"
                        >
                            {visibleCommands.map((cmd, i) => (
                                <button
                                    key={i}
                                    onClick={() => executeCommand(cmd.cmd)}
                                    className="w-full flex items-center gap-3 px-4 py-3 hover:bg-neutral-800 text-left transition-colors border-b border-neutral-800/50 last:border-0"
                                >
                                    <div className="bg-neutral-800 p-2 rounded-lg text-neutral-400">
                                        <cmd.icon size={18} />
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium text-white">{cmd.cmd}</p>
                                        <p className="text-xs text-neutral-400">{cmd.desc}</p>
                                    </div>
                                </button>
                            ))}
                        </motion.div>
                    )}
                </AnimatePresence>

                <div className="relative bg-neutral-900 rounded-xl border border-neutral-800 shadow-xl">
                    <div className="overflow-y-auto">
                        <Textarea
                            ref={textareaRef}
                            value={value}
                            onChange={handleInputChange}
                            onKeyDown={handleKeyDown}
                            placeholder="Ask admin agent..."
                            className={cn(
                                "w-full px-4 py-4",
                                "resize-none",
                                "bg-transparent",
                                "border-none",
                                "text-white text-sm focus-visible:ring-0 focus-visible:ring-offset-0",
                                "placeholder:text-neutral-500"
                            )}
                        />
                    </div>

                    <div className="flex items-center justify-between px-3 pb-3">
                        <div className="flex items-center gap-1">
                            <button
                                type="button"
                                className="p-2 rounded-lg text-neutral-400 hover:text-white hover:bg-neutral-800 transition-colors"
                            >
                                <Paperclip className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="flex items-center gap-2">
                            <button
                                type="button"
                                onClick={() => value.trim() && sendMessage(value.trim())}
                                className={cn(
                                    "p-2 rounded-lg transition-colors",
                                    value.trim()
                                        ? "bg-white text-black hover:bg-neutral-200"
                                        : "bg-neutral-800 text-neutral-500"
                                )}
                            >
                                <ArrowUpIcon className="w-5 h-5" />
                            </button>
                        </div>
                    </div>
                </div>

                {messages.length === 0 && (
                    <div className="flex items-center justify-center gap-3 mt-6 flex-wrap">
                        <button onClick={() => sendMessage("/status")} className="flex items-center gap-2 px-4 py-2 bg-neutral-100 dark:bg-neutral-900 hover:bg-neutral-200 dark:hover:bg-neutral-800 rounded-full border border-neutral-200 dark:border-neutral-800 transition-colors text-neutral-400 hover:text-white">
                            <Activity className="w-4 h-4" />
                            <span className="text-sm">Status PM2</span>
                        </button>
                        <button onClick={() => sendMessage("/logs 10")} className="flex items-center gap-2 px-4 py-2 bg-neutral-100 dark:bg-neutral-900 hover:bg-neutral-200 dark:hover:bg-neutral-800 rounded-full border border-neutral-200 dark:border-neutral-800 transition-colors text-neutral-400 hover:text-white">
                            <TerminalSquare className="w-4 h-4" />
                            <span className="text-sm">Server Logs</span>
                        </button>
                        <button onClick={() => sendMessage("/agent change")} className="flex items-center gap-2 px-4 py-2 bg-neutral-100 dark:bg-neutral-900 hover:bg-neutral-200 dark:hover:bg-neutral-800 rounded-full border border-neutral-200 dark:border-neutral-800 transition-colors text-neutral-400 hover:text-white">
                            <Bot className="w-4 h-4" />
                            <span className="text-sm">Cambiar Agente</span>
                        </button>
                        <button onClick={() => sendMessage("/test firby")} className="flex items-center gap-2 px-4 py-2 bg-neutral-100 dark:bg-neutral-900 hover:bg-neutral-200 dark:hover:bg-neutral-800 rounded-full border border-neutral-200 dark:border-neutral-800 transition-colors text-neutral-400 hover:text-white">
                            <RefreshCw className="w-4 h-4" />
                            <span className="text-sm">Testear Firby</span>
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
