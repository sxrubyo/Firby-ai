"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageSquare, X, Send, Sparkles, Minus, Bot, User, ArrowRight, RefreshCw } from "lucide-react";
import LatticeLoader from "./LatticeLoader";

interface Message {
  id: string;
  sender: "user" | "firby";
  text: string;
  time: string;
}

const QUICK_SUGGESTIONS = [
  "Quiero cambiar mi correo",
  "¿Qué tratamientos tienen?",
  "Quiero agendar una cita",
  "¿Cuáles son los horarios?",
];

export function FirbyChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome-1",
      sender: "firby",
      text: "¡Hola! Soy Firby, el agente inteligente de la clínica.",
      time: "Ahora",
    },
    {
      id: "welcome-2",
      sender: "firby",
      text: "¿En qué te puedo colaborar hoy? Puedo ayudarte a agendar citas, consultar tratamientos o resolver solicitudes en tiempo real.",
      time: "Ahora",
    },
  ]);

  const [sessionId, setSessionId] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    let sid = sessionStorage.getItem("firby_widget_session");
    if (!sid) {
      sid = "web_" + Math.random().toString(36).substring(2, 9);
      sessionStorage.setItem("firby_widget_session", sid);
    }
    setSessionId(sid);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [isOpen, messages, loading]);

  const sendMessage = async (textToSend?: string) => {
    const message = (textToSend || input).trim();
    if (!message || loading) return;

    const userMsg: Message = {
      id: "user-" + Date.now(),
      sender: "user",
      text: message,
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/widget/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message,
          user_id: sessionId || "web_visitor",
        }),
      });

      const data = await res.json();
      if (data.ok && data.bubbles && Array.isArray(data.bubbles)) {
        // Render each bubble with staggered realistic timing
        data.bubbles.forEach((bubbleText: string, idx: number) => {
          setTimeout(() => {
            setMessages((prev) => [
              ...prev,
              {
                id: `firby-${Date.now()}-${idx}`,
                sender: "firby",
                text: bubbleText,
                time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
              },
            ]);
          }, idx * 300);
        });
      } else if (data.response) {
        setMessages((prev) => [
          ...prev,
          {
            id: `firby-${Date.now()}`,
            sender: "firby",
            text: data.response,
            time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            id: `firby-err-${Date.now()}`,
            sender: "firby",
            text: "No pude procesar tu mensaje en este momento. Por favor intenta de nuevo.",
            time: "Ahora",
          },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: `firby-err-${Date.now()}`,
          sender: "firby",
          text: "Hubo un problema de conexión con el agente. Verifica tu conexión.",
          time: "Ahora",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 font-sans select-none">
      {/* VENTANA DEL CHAT */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.88, y: 20, transformOrigin: "bottom right" }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.88, y: 20 }}
            transition={{ type: "spring", damping: 25, stiffness: 280 }}
            className="w-[360px] sm:w-[400px] h-[550px] max-h-[82vh] mb-3.5 rounded-3xl bg-white dark:bg-[#121216] border border-neutral-200 dark:border-[#222228] shadow-[0_20px_50px_rgba(0,0,0,0.22)] dark:shadow-[0_20px_50px_rgba(0,0,0,0.65)] flex flex-col overflow-hidden"
          >
            {/* CABECERA */}
            <div className="px-4 py-3.5 bg-neutral-900 dark:bg-[#09090b] text-white flex items-center justify-between border-b border-neutral-800">
              <div className="flex items-center gap-2.5">
                <div className="relative">
                  <img
                    src="/brand-assets/firby-isotype.png?v=20261004_chat_negro"
                    alt="Firby"
                    className="w-9 h-9 rounded-full object-contain shadow-xs select-none"
                  />
                  <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-[#10b981] ring-2 ring-neutral-900 animate-pulse" />
                </div>
                <div>
                  <div className="flex items-center gap-1.5">
                    <h3 className="font-semibold text-sm leading-tight text-white">Firby AI</h3>
                    <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-[#b9fa01]/20 text-[#b9fa01] font-mono font-medium">
                      Activo
                    </span>
                  </div>
                  <p className="text-[11px] text-neutral-400 leading-tight mt-0.5">
                    Agente Clínico Autónomo
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-1">
                <button
                  type="button"
                  onClick={() => setIsOpen(false)}
                  className="p-1.5 rounded-lg text-neutral-400 hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
                  title="Minimizar"
                >
                  <Minus className="w-4 h-4" />
                </button>
                <button
                  type="button"
                  onClick={() => setIsOpen(false)}
                  className="p-1.5 rounded-lg text-neutral-400 hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
                  title="Cerrar chat"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* CUERPO DE MENSAJES */}
            <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-[#fafafa] dark:bg-[#0e0e11] custom-scrollbar">
              {messages.map((m) => {
                const isUser = m.sender === "user";
                return (
                  <div
                    key={m.id}
                    className={`flex items-end gap-2 ${isUser ? "justify-end" : "justify-start"}`}
                  >
                    {!isUser && (
                      <img
                        src="/brand-assets/firby-isotype.png?v=20261004_chat_negro"
                        alt="Firby"
                        className="w-6 h-6 rounded-full object-contain shrink-0 mb-1 select-none"
                      />
                    )}
                    <div
                      className={`max-w-[78%] rounded-2xl px-3.5 py-2.5 text-xs sm:text-[13px] leading-relaxed shadow-2xs ${
                        isUser
                          ? "bg-[#b9fa01] text-black font-medium rounded-br-xs"
                          : "bg-white dark:bg-[#1a1a20] text-neutral-800 dark:text-neutral-100 border border-neutral-200 dark:border-[#27272f] rounded-bl-xs"
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{m.text}</p>
                      <div
                        className={`text-[9px] mt-1 text-right ${
                          isUser ? "text-neutral-800/70" : "text-neutral-400"
                        }`}
                      >
                        {m.time}
                      </div>
                    </div>
                  </div>
                );
              })}

              {/* INDICADOR DE ESCRITURA */}
              {loading && (
                <div className="flex items-end gap-2 justify-start">
                  <div className="w-6 h-6 rounded-lg bg-[#b9fa01] text-black flex items-center justify-center text-[10px] font-bold shrink-0 mb-1">
                    F
                  </div>
                  <div className="bg-white dark:bg-[#1a1a20] border border-neutral-200 dark:border-[#27272f] rounded-2xl rounded-bl-xs px-3.5 py-2.5 shadow-2xs flex items-center">
                    <LatticeLoader
                      status="working"
                      label="Thinking"
                      doneLabel="Done in"
                      pattern="orbit"
                      grid={3}
                      shape="round"
                      cellSize={5}
                      gap={2}
                      fontSize={13}
                      step={90}
                      idleOpacity={0.15}
                      glow={false}
                      showTimer={true}
                    />
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* CHIPS DE SUGERENCIAS RÁPIDAS */}
            {messages.length <= 4 && !loading && (
              <div className="px-3 py-2 bg-white/70 dark:bg-[#121216]/70 border-t border-neutral-100 dark:border-[#1a1a20] flex items-center gap-1.5 overflow-x-auto custom-scrollbar">
                {QUICK_SUGGESTIONS.map((sug, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => sendMessage(sug)}
                    className="shrink-0 text-[11px] px-2.5 py-1 rounded-full bg-neutral-100 dark:bg-neutral-800 hover:bg-[#b9fa01] hover:text-black dark:hover:bg-[#b9fa01] dark:hover:text-black text-neutral-700 dark:text-neutral-300 transition-all cursor-pointer border border-neutral-200 dark:border-neutral-700"
                  >
                    {sug}
                  </button>
                ))}
              </div>
            )}

            {/* CAMPO DE ENTRADA */}
            <div className="p-3 bg-white dark:bg-[#121216] border-t border-neutral-200 dark:border-[#1e1e24] flex items-center gap-2">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Escribe un mensaje a Firby..."
                disabled={loading}
                className="flex-1 bg-neutral-100 dark:bg-[#18181f] border border-neutral-200 dark:border-[#27272f] focus:border-[#b9fa01] rounded-xl px-3.5 py-2 text-xs sm:text-[13px] text-neutral-900 dark:text-neutral-100 placeholder:text-neutral-400 outline-none transition-colors"
              />
              <button
                type="button"
                onClick={() => sendMessage()}
                disabled={!input.trim() || loading}
                className={`p-2.5 rounded-xl transition-all flex items-center justify-center cursor-pointer ${
                  input.trim() && !loading
                    ? "bg-[#b9fa01] text-black shadow-xs hover:brightness-105 active:scale-95"
                    : "bg-neutral-100 dark:bg-neutral-800 text-neutral-400 cursor-not-allowed"
                }`}
                title="Enviar mensaje"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>

            {/* FOOTER DISCRETO */}
            <div className="py-1 px-3 bg-neutral-50 dark:bg-[#0b0b0e] text-center border-t border-neutral-100 dark:border-[#16161c]">
              <span className="text-[10px] text-neutral-400 font-mono">
                Firby Autonomous Clinical Agent v2.5
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* BOTÓN FLOTANTE (TRIGGER CIRCULAR) */}
      <motion.button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        whileHover={{ scale: 1.06 }}
        whileTap={{ scale: 0.94 }}
        className={`relative flex items-center justify-center shadow-[0_8px_30px_rgba(0,0,0,0.35)] transition-all cursor-pointer ${
          isOpen
            ? "w-13 h-13 rounded-2xl bg-neutral-900 dark:bg-[#18181c] text-white border border-neutral-700"
            : "w-14 h-14 rounded-full bg-[#b9fa01] text-black border-2 border-black/10 dark:border-white/10"
        }`}
        title={isOpen ? "Cerrar chat" : "Chatear con Firby AI"}
        aria-label={isOpen ? "Cerrar chat" : "Chatear con Firby AI"}
      >
        {/* PULSO ACTIVO CUANDO ESTÁ CERRADO */}
        {!isOpen && (
          <span className="absolute -top-0.5 -right-0.5 flex h-3.5 w-3.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-emerald-500 border-2 border-white dark:border-[#0e0e11]" />
          </span>
        )}

        <AnimatePresence mode="wait" initial={false}>
          {isOpen ? (
            <motion.div
              key="close-icon"
              initial={{ rotate: -90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: 90, opacity: 0 }}
              transition={{ duration: 0.15 }}
            >
              <X className="w-5 h-5 text-white" />
            </motion.div>
          ) : (
            <motion.div
              key="chat-icon"
              initial={{ scale: 0.7, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.7, opacity: 0 }}
              transition={{ duration: 0.15 }}
              className="flex items-center justify-center"
            >
              <MessageSquare className="w-6 h-6 text-black fill-black" />
            </motion.div>
          )}
        </AnimatePresence>
      </motion.button>
    </div>
  );
}
