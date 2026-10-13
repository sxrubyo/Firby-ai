"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import {
  ArrowUpIcon,
  Phone,
  User,
  RefreshCw,
  Send,
  Loader2,
  Calendar,
  Tag,
  Clock,
  Sparkles,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface PatientProfile {
  chat_id: string;
  name?: string;
  phone?: string;
  visits?: number;
  first_seen?: string;
  last_seen?: string;
  tags?: string[];
  preferences?: Record<string, any>;
}

interface Message {
  id: string;
  role: "user" | "assistant" | "admin";
  content: string;
  ts?: string;
}

export function PatientChatWindow({ chatId }: { chatId: string | null }) {
  const [value, setValue] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [patient, setPatient] = useState<PatientProfile | null>(null);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [escalationNeeded, setEscalationNeeded] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const reactivateBot = async () => {
    if (!chatId) return;
    try {
      const token = localStorage.getItem("firby_master_key") || localStorage.getItem("dev_master_key") || "";
      const res = await fetch(`/conversations/patient/${chatId}/reactivate`, {
        method: "POST",
        headers: { "x-master-key": token }
      });
      if (res.ok) {
        setEscalationNeeded(false);
        fetchChatData(true);
      }
    } catch (e) {
      console.error("Error reactivating bot:", e);
    }
  };

  // Fetch patient profile and conversation history
  const fetchChatData = useCallback(async (isSilent = false) => {
    if (!chatId) return;
    if (!isSilent) setLoading(true);
    else setRefreshing(true);

    try {
      const token = localStorage.getItem("firby_master_key") || localStorage.getItem("dev_master_key") || "";
      
      // 1. Fetch Patient Detail (with fallback to simple profile if 404)
      let patientData: PatientProfile = { chat_id: chatId };
      try {
        const patientRes = await fetch(`/patients/${chatId}`, {
          headers: { "x-master-key": token }
        });
        if (patientRes.ok) {
          patientData = await patientRes.json();
        }
      } catch (e) {
        console.error("Error fetching patient detail:", e);
      }
      setPatient(patientData);

      // 2. Fetch Conversation History
      const historyRes = await fetch(`/conversations/patient/${chatId}`, {
        headers: { "x-master-key": token }
      });
      if (historyRes.ok) {
        const data = await historyRes.json();
        setEscalationNeeded(data.escalation_needed || false);
        if (data.messages) {
          const loaded: Message[] = data.messages.map((m: any, i: number) => ({
            id: `msg-${i}-${m.ts}`,
            role: m.role || "user",
            content: m.content || m.text || "",
            ts: m.ts
          }));
          setMessages(loaded);
        }
      }
    } catch (e) {
      console.error("Error fetching chat data:", e);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [chatId]);

  // Initial load
  useEffect(() => {
    fetchChatData(false);
  }, [chatId, fetchChatData]);

  // Polling for new messages every 4 seconds
  useEffect(() => {
    if (!chatId) return;
    const interval = setInterval(() => {
      fetchChatData(true);
    }, 4000);
    return () => clearInterval(interval);
  }, [chatId, fetchChatData]);

  // Scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (value.trim() && !sending) {
        sendMessage(value.trim());
      }
    }
  };

  const sendMessage = async (text: string) => {
    if (!chatId || sending) return;
    setSending(true);
    setValue("");

    // Append to local state immediately
    const tempId = `temp-${Date.now()}`;
    const newMsg: Message = { id: tempId, role: "admin", content: text, ts: new Date().toISOString() };
    setMessages(prev => [...prev, newMsg]);

    try {
      const token = localStorage.getItem("firby_master_key") || localStorage.getItem("dev_master_key") || "";
      const res = await fetch("/send-message", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-master-key": token
        },
        body: JSON.stringify({
          chat_id: chatId,
          message: text,
          confirmar: true
        })
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || "Error al enviar mensaje");
      }

      // Refresh to get official timestamp and confirm delivery
      fetchChatData(true);
    } catch (e: any) {
      console.error("Error sending message:", e);
      // Mark temporary message with error
      setMessages(prev =>
        prev.map(m => m.id === tempId ? { ...m, content: `${m.content}\n⚠️ (Error al enviar)` } : m)
      );
    } finally {
      setSending(false);
      if (textareaRef.current) {
        textareaRef.current.focus();
      }
    }
  };

  // Format date helper
  const formatTime = (tsStr?: string) => {
    if (!tsStr) return "";
    try {
      const date = new Date(tsStr);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch (e) {
      return "";
    }
  };

  // Clean chat_id to display clean phone number
  const displayPhone = (cid: string) => {
    return cid.split("@")[0];
  };

  if (!chatId) {
    return (
      <div className="flex flex-col items-center justify-center w-full h-full text-center px-4 bg-[#fafafa] dark:bg-[#0a0a0c] text-neutral-500 dark:text-neutral-400">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
          className="max-w-md space-y-4 flex flex-col items-center"
        >
          <div className="h-16 w-16 rounded-3xl bg-neutral-100 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 flex items-center justify-center text-neutral-400 dark:text-neutral-500 shadow-sm mb-2">
            <User className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-bold text-neutral-800 dark:text-neutral-200">Buzón de Pacientes</h2>
          <p className="text-sm">
            Selecciona un paciente del menú lateral para revisar su historial de chat de WhatsApp y enviarle mensajes de forma directa.
          </p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="flex flex-col w-full h-full bg-[#fafafa] dark:bg-[#0a0a0c] overflow-hidden relative">
      {/* Header */}
      <div className="h-16 border-b border-neutral-200 dark:border-neutral-800/80 bg-white/50 dark:bg-[#111112]/50 backdrop-blur-md flex items-center justify-between px-6 z-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-[#e05a2b]/10 text-[#e05a2b] flex items-center justify-center font-bold text-base border border-[#e05a2b]/20">
            {patient?.name ? patient.name.charAt(0) : <User className="w-5 h-5" />}
          </div>
          <div className="flex flex-col">
            <span className="font-semibold text-neutral-900 dark:text-neutral-100 text-sm leading-tight">
              {patient?.name || displayPhone(chatId)}
            </span>
            <span className="text-xs text-neutral-400 flex items-center gap-1.5 mt-0.5 font-mono">
              <Phone className="w-3 h-3" /> {displayPhone(chatId)}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {refreshing && (
            <span className="text-[11px] text-neutral-400 flex items-center gap-1">
              <Loader2 className="w-3.5 h-3.5 animate-spin" /> Actualizando...
            </span>
          )}
          <button
            onClick={() => fetchChatData(false)}
            className="p-2 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-lg transition-colors"
            title="Actualizar chat"
          >
            <RefreshCw className={cn("w-4 h-4", loading && "animate-spin")} />
          </button>
        </div>
      </div>

      {escalationNeeded && (
        <div className="bg-amber-500/10 border-b border-amber-500/20 px-6 py-2.5 flex items-center justify-between text-xs text-amber-800 dark:text-amber-300 z-10">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-amber-500 animate-pulse" />
            <span><strong>Asistente IA Pausado:</strong> El cliente solicitó atención humana. Firby no responderá automáticamente en este chat.</span>
          </div>
          <button
            onClick={reactivateBot}
            className="px-3 py-1 bg-amber-500 hover:bg-amber-600 active:bg-amber-700 text-white rounded font-medium transition-colors cursor-pointer"
          >
            Reactivar agente
          </button>
        </div>
      )}

      {/* Main chat layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Messages */}
        <div className="flex-grow flex flex-col justify-between overflow-hidden relative">
          {loading ? (
            <div className="flex-grow flex items-center justify-center">
              <Loader2 className="w-8 h-8 text-[#e05a2b] animate-spin" />
            </div>
          ) : (
            <div
              ref={scrollRef}
              className="flex-grow overflow-y-auto px-6 py-6 space-y-4 custom-scrollbar bg-neutral-50/50 dark:bg-black/10"
            >
              {messages.length === 0 ? (
                <div className="h-full flex items-center justify-center text-center text-sm text-neutral-400">
                  Sin mensajes registrados en esta conversación.
                </div>
              ) : (
                messages.map((msg) => {
                  const isPatient = msg.role === "user";
                  const isAI = msg.role === "assistant";
                  return (
                    <motion.div
                      key={msg.id}
                      initial={{ opacity: 0, y: 5 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={cn(
                        "flex w-full flex-col",
                        isPatient ? "items-start" : "items-end"
                      )}
                    >
                      <div className="flex items-center gap-1.5 mb-1 px-1">
                        {isAI && (
                          <span className="text-[9px] font-bold text-violet-500 bg-violet-500/10 px-1.5 py-0.5 rounded flex items-center gap-0.5">
                            <Sparkles className="w-2.5 h-2.5" /> Firby (AI)
                          </span>
                        )}
                        {!isPatient && !isAI && (
                          <span className="text-[9px] font-bold text-emerald-500 bg-emerald-500/10 px-1.5 py-0.5 rounded">
                            Tú (Manual)
                          </span>
                        )}
                      </div>
                      
                      <div
                        className={cn(
                          "max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap shadow-sm",
                          isPatient
                            ? "bg-white dark:bg-[#1a1a1c] text-neutral-900 dark:text-neutral-100 rounded-tl-sm border border-neutral-200 dark:border-neutral-800/80"
                            : isAI
                            ? "bg-violet-950/20 dark:bg-violet-950/40 text-violet-900 dark:text-violet-200 rounded-tr-sm border border-violet-500/20"
                            : "bg-[#e05a2b] text-white rounded-tr-sm"
                        )}
                      >
                        {msg.content}
                        <div
                          className={cn(
                            "text-[10px] mt-1 text-right block",
                            isPatient
                              ? "text-neutral-400"
                              : isAI
                              ? "text-violet-400"
                              : "text-white/70"
                          )}
                        >
                          {formatTime(msg.ts)}
                        </div>
                      </div>
                    </motion.div>
                  );
                })
              )}
            </div>
          )}

          {/* Input Bar */}
          <div className="p-4 bg-white/70 dark:bg-[#0a0a0c]/70 backdrop-blur-md border-t border-neutral-200 dark:border-neutral-800/80">
            <div className="relative flex items-end gap-2 bg-white dark:bg-[#111113] rounded-xl border border-neutral-200 dark:border-neutral-800 px-3 py-2 focus-within:border-[#e05a2b] transition-all">
              <Textarea
                ref={textareaRef}
                value={value}
                onChange={(e) => setValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Escribe un mensaje de WhatsApp..."
                disabled={sending}
                className="w-full min-h-[40px] max-h-[160px] py-1 resize-none bg-transparent border-0 focus-visible:ring-0 focus-visible:ring-offset-0 text-sm text-neutral-900 dark:text-white placeholder:text-neutral-500"
              />
              <button
                onClick={() => value.trim() && sendMessage(value.trim())}
                disabled={sending || !value.trim()}
                className={cn(
                  "p-2.5 rounded-lg transition-colors flex-shrink-0",
                  value.trim() && !sending
                    ? "bg-[#e05a2b] text-white hover:bg-[#c94e24]"
                    : "bg-neutral-100 dark:bg-neutral-800 text-neutral-400"
                )}
              >
                {sending ? (
                  <Loader2 className="w-4.5 h-4.5 animate-spin" />
                ) : (
                  <Send className="w-4.5 h-4.5" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Right Sidebar - Patient Info */}
        <div className="w-64 border-l border-neutral-200 dark:border-neutral-800/80 bg-white/30 dark:bg-neutral-900/10 hidden lg:flex flex-col p-6 overflow-y-auto custom-scrollbar gap-6">
          <div className="flex flex-col items-center text-center">
            <div className="w-16 h-16 rounded-full bg-[#e05a2b]/10 text-[#e05a2b] flex items-center justify-center font-bold text-2xl border border-[#e05a2b]/20 mb-3 shadow-sm">
              {patient?.name ? patient.name.charAt(0) : <User className="w-8 h-8" />}
            </div>
            <h3 className="font-semibold text-neutral-900 dark:text-neutral-100 text-base leading-tight">
              {patient?.name || "Paciente"}
            </h3>
            <span className="text-xs text-neutral-400 mt-1 font-mono">{displayPhone(chatId)}</span>
          </div>

          <hr className="border-neutral-200 dark:border-neutral-800" />

          {/* Stats */}
          <div className="space-y-4">
            <h4 className="text-[11px] font-bold text-neutral-400 uppercase tracking-wider">Historial</h4>
            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between text-neutral-500">
                <span className="flex items-center gap-1.5"><Calendar className="w-3.5 h-3.5" /> Primera visita</span>
                <span className="font-medium text-neutral-900 dark:text-neutral-200 text-right">
                  {patient?.first_seen ? new Date(patient.first_seen).toLocaleDateString() : "-"}
                </span>
              </div>
              <div className="flex items-center justify-between text-neutral-500">
                <span className="flex items-center gap-1.5"><Clock className="w-3.5 h-3.5" /> Última actividad</span>
                <span className="font-medium text-neutral-900 dark:text-neutral-200 text-right">
                  {patient?.last_seen ? new Date(patient.last_seen).toLocaleDateString() : "-"}
                </span>
              </div>
            </div>
          </div>

          {/* Tags */}
          {patient?.tags && patient.tags.length > 0 && (
            <div className="space-y-3">
              <h4 className="text-[11px] font-bold text-neutral-400 uppercase tracking-wider flex items-center gap-1.5">
                <Tag className="w-3.5 h-3.5" /> Etiquetas
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {patient.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-0.5 bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-300 rounded text-[11px] font-medium"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Preferences */}
          {patient?.preferences && Object.keys(patient.preferences).length > 0 && (
            <div className="space-y-3">
              <h4 className="text-[11px] font-bold text-neutral-400 uppercase tracking-wider">Preferencias</h4>
              <div className="space-y-2 text-xs">
                {Object.entries(patient.preferences).map(([key, value]) => (
                  <div key={key} className="flex flex-col bg-neutral-100/50 dark:bg-neutral-800/40 p-2 rounded">
                    <span className="text-[10px] text-neutral-400 capitalize">{key}</span>
                    <span className="font-medium text-neutral-800 dark:text-neutral-200 mt-0.5">
                      {typeof value === "object" ? JSON.stringify(value) : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
