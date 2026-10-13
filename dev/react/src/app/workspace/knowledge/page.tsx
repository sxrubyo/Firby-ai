"use client";

import React, { useState, useEffect } from "react";
import { playSound } from "@/lib/sound";
import { AppShell } from "@/components/app-shell";
import { Button } from "@/components/ui/button";
import {
  Users,
  Sliders,
  Database,
  TrendingUp,
  Key,
  Volume2,
  CheckCircle2,
  AlertCircle,
  Search,
  Sparkles,
  RefreshCw,
  Plus,
  Send,
  ExternalLink,
  Shield,
  Layers,
  ArrowRight,
  Clock,
  Phone,
  Calendar,
  Code
} from "lucide-react";

type ControlTab = "roles" | "prompt" | "memory" | "growth" | "vault" | "voice";

interface EmployeeRoleItem {
  id: string;
  title: string;
  default_name: string;
  description: string;
  skills: string[];
  is_active: boolean;
}

interface VaultIntegration {
  id: string;
  name: string;
  category: string;
  docs: string;
  is_configured: boolean;
  masked_token?: string | null;
  updated_at?: string | null;
}

interface GrowthLead {
  id: string | number;
  chat_id: string;
  name: string;
  phone: string;
  email: string;
  last_service: string;
  last_seen: string;
  status: string;
  inactivity_days: number;
}

interface MemorySearchResult {
  id: number;
  session_id: string;
  chat_id: string;
  role: string;
  content: string;
  timestamp: number;
  rank: number;
}

export default function WorkspaceKnowledgePage() {
  const [activeTab, setActiveTab] = useState<ControlTab>("roles");
  const [tenantId] = useState("growsantix");

  // Notifications
  const [statusMessage, setStatusMessage] = useState<{ text: string; type: "success" | "error" | "info" } | null>(null);

  // Tab 1: Roles
  const [roles, setRoles] = useState<EmployeeRoleItem[]>([]);
  const [activeRole, setActiveRole] = useState<string>("recepcionista");
  const [loadingRoles, setLoadingRoles] = useState(false);
  const [updatingRole, setUpdatingRole] = useState(false);

  // Tab 2: Prompt & Voice Accent
  const [agentName, setAgentName] = useState("Firby");
  const [systemPrompt, setSystemPrompt] = useState("");
  const [voiceAccent, setVoiceAccent] = useState("general");
  const [operationalLimits, setOperationalLimits] = useState<string[]>([]);
  const [savingConfig, setSavingConfig] = useState(false);

  // Tab 3: Memory FTS5
  const [memoryQuery, setMemoryQuery] = useState("");
  const [memoryResults, setMemoryResults] = useState<MemorySearchResult[]>([]);
  const [searchingMemory, setSearchingMemory] = useState(false);
  const [memoryStats, setMemoryStats] = useState<{ total_msgs: number; total_sess: number; raw_convs: number } | null>(null);
  const [newMemoryContent, setNewMemoryContent] = useState("");
  const [addingMemory, setAddingMemory] = useState(false);

  // Tab 4: Growth Engine
  const [leads, setLeads] = useState<GrowthLead[]>([]);
  const [loadingLeads, setLoadingLeads] = useState(false);
  const [inactivityDays, setInactivityDays] = useState(30);
  const [campaignServiceName, setCampaignServiceName] = useState("Revisión y Seguimiento");
  const [campaignOffer, setCampaignOffer] = useState("Revisión prioritaria sin costo de apertura");
  const [campaignPreviews, setCampaignPreviews] = useState<any[]>([]);
  const [generatingCampaign, setGeneratingCampaign] = useState(false);

  // Tab 5: Vault & Executor
  const [vaultIntegrations, setVaultIntegrations] = useState<VaultIntegration[]>([]);
  const [loadingVault, setLoadingVault] = useState(false);
  const [selectedService, setSelectedService] = useState("notion");
  const [apiKeyInput, setApiKeyInput] = useState("");
  const [savingKey, setSavingKey] = useState(false);
  const [testUrl, setTestUrl] = useState("https://api.notion.com/v1/users/me");
  const [testMethod, setTestMethod] = useState("GET");
  const [testResult, setTestResult] = useState<any>(null);
  const [executingTest, setExecutingTest] = useState(false);

  // Tab 6: Audio Auditor
  const [audioScript, setAudioScript] = useState("Hola, te llamo para confirmar tu cita médica programada para este viernes a las 3 de la tarde.");
  const [auditorAccent, setAuditorAccent] = useState("paisa");
  const [auditedScript, setAuditedScript] = useState<any>(null);
  const [auditingAudio, setAuditingAudio] = useState(false);

  const showNotification = (text: string, type: "success" | "error" | "info" = "success") => {
    setStatusMessage({ text, type });
    playSound("pop");
    setTimeout(() => setStatusMessage(null), 4000);
  };

  // Fetch initial data
  useEffect(() => {
    fetchRoles();
    fetchAgentConfig();
    fetchMemoryStats();
  }, []);

  useEffect(() => {
    if (activeTab === "growth") fetchLeads(inactivityDays);
    if (activeTab === "vault") fetchVault();
  }, [activeTab]);

  const fetchRoles = async () => {
    setLoadingRoles(true);
    try {
      const res = await fetch(`/api/workspace/employee-roles?tenant_id=${tenantId}`);
      const data = await res.json();
      if (data.ok) {
        setRoles(data.roles || []);
        setActiveRole(data.active_role || "recepcionista");
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingRoles(false);
    }
  };

  const handleSelectRole = async (roleId: string) => {
    setUpdatingRole(true);
    try {
      const res = await fetch("/api/workspace/employee-roles/select", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tenant_id: tenantId, role: roleId })
      });
      const data = await res.json();
      if (data.ok) {
        setActiveRole(roleId);
        setRoles(prev => prev.map(r => ({ ...r, is_active: r.id === roleId })));
        showNotification(data.message || `Rol ${roleId} activado exitosamente.`);
      } else {
        showNotification(data.error || "Error al cambiar el rol.", "error");
      }
    } catch (e: any) {
      showNotification(e.message, "error");
    } finally {
      setUpdatingRole(false);
    }
  };

  const fetchAgentConfig = async () => {
    try {
      const res = await fetch(`/api/workspace/agent-config?tenant_id=${tenantId}`);
      const data = await res.json();
      if (data.ok) {
        setAgentName(data.name || "Firby");
        setSystemPrompt(data.system_prompt || "");
        setVoiceAccent(data.voice_accent || "general");
        setOperationalLimits(data.operational_limits || []);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleSaveConfig = async () => {
    setSavingConfig(true);
    try {
      const res = await fetch("/api/workspace/agent-config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tenant_id: tenantId,
          name: agentName,
          prompt: systemPrompt,
          voice_accent: voiceAccent,
          operational_limits: operationalLimits
        })
      });
      const data = await res.json();
      if (data.ok) {
        showNotification("Configuración de agente y directivas guardadas en caliente.");
      } else {
        showNotification(data.error || "Error al guardar.", "error");
      }
    } catch (e: any) {
      showNotification(e.message, "error");
    } finally {
      setSavingConfig(false);
    }
  };

  const fetchMemoryStats = async () => {
    try {
      const res = await fetch("/api/workspace/memory/stats");
      const data = await res.json();
      if (data.ok) {
        setMemoryStats({
          total_msgs: data.fts_messages_indexed,
          total_sess: data.fts_sessions_active,
          raw_convs: data.raw_conversations_total
        });
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleSearchMemory = async () => {
    if (!memoryQuery.trim()) return;
    setSearchingMemory(true);
    try {
      const res = await fetch(`/api/workspace/memory/search?query=${encodeURIComponent(memoryQuery)}&limit=15`);
      const data = await res.json();
      if (data.ok) {
        setMemoryResults(data.results || []);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setSearchingMemory(false);
    }
  };

  const handleAddMemory = async () => {
    if (!newMemoryContent.trim()) return;
    setAddingMemory(true);
    try {
      const res = await fetch("/api/workspace/memory/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: newMemoryContent, role: "system", tenant_id: tenantId })
      });
      const data = await res.json();
      if (data.ok) {
        showNotification("Hecho indexado en la memoria persistente FTS5.");
        setNewMemoryContent("");
        fetchMemoryStats();
      } else {
        showNotification(data.error || "Error al indexar.", "error");
      }
    } catch (e: any) {
      showNotification(e.message, "error");
    } finally {
      setAddingMemory(false);
    }
  };

  const fetchLeads = async (days: number) => {
    setLoadingLeads(true);
    try {
      const res = await fetch(`/api/workspace/growth/leads?days_inactive=${days}&limit=20`);
      const data = await res.json();
      if (data.ok) {
        setLeads(data.leads || []);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingLeads(false);
    }
  };

  const handleGenerateCampaignPreview = async () => {
    setGeneratingCampaign(true);
    try {
      const res = await fetch("/api/workspace/growth/campaign/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          service_name: campaignServiceName,
          clinic_name: "Firby AI",
          custom_offer: campaignOffer,
          limit: 4
        })
      });
      const data = await res.json();
      if (data.ok) {
        setCampaignPreviews(data.previews || []);
        showNotification("Simulación de campaña generada con ritmo anti-baneo.");
      }
    } catch (e: any) {
      showNotification(e.message, "error");
    } finally {
      setGeneratingCampaign(false);
    }
  };

  const fetchVault = async () => {
    setLoadingVault(true);
    try {
      const res = await fetch("/api/workspace/integrations/vault");
      const data = await res.json();
      if (data.ok) {
        setVaultIntegrations(data.integrations || []);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingVault(false);
    }
  };

  const handleSaveVaultKey = async () => {
    if (!apiKeyInput.trim()) return;
    setSavingKey(true);
    try {
      const res = await fetch("/api/workspace/integrations/vault", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ service: selectedService, api_key: apiKeyInput, tenant_id: tenantId })
      });
      const data = await res.json();
      if (data.ok) {
        showNotification(`Credencial vinculada para ${selectedService}.`);
        setApiKeyInput("");
        fetchVault();
      } else {
        showNotification(data.error || "Error al guardar credencial.", "error");
      }
    } catch (e: any) {
      showNotification(e.message, "error");
    } finally {
      setSavingKey(false);
    }
  };

  const handleExecuteHttpTest = async () => {
    if (!testUrl.trim()) return;
    setExecutingTest(true);
    setTestResult(null);
    try {
      const res = await fetch("/api/workspace/integrations/vault/test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: testUrl, method: testMethod, service_hint: selectedService })
      });
      const data = await res.json();
      setTestResult(data);
      if (data.success) {
        showNotification(`Llamada HTTP exitosa (${data.status_code}).`);
      } else {
        showNotification(`Fallo HTTP: ${data.error || data.status_code}`, "error");
      }
    } catch (e: any) {
      showNotification(e.message, "error");
    } finally {
      setExecutingTest(false);
    }
  };

  const handleAuditAudio = async () => {
    if (!audioScript.trim()) return;
    setAuditingAudio(true);
    try {
      const res = await fetch("/api/workspace/audio/audit-script", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: audioScript, accent: auditorAccent })
      });
      const data = await res.json();
      if (data.ok) {
        setAuditedScript(data);
        showNotification("Guion fonético refinado con naturalidad regional.");
      }
    } catch (e: any) {
      showNotification(e.message, "error");
    } finally {
      setAuditingAudio(false);
    }
  };

  return (
    <AppShell fullWidth={true}>
      <div className="max-w-7xl mx-auto space-y-8 pb-16">
        {/* HEADER PRINCIPAL */}
        <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-2xl p-6 sm:p-8 shadow-xs">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="h-2 w-2 rounded-full bg-[#b9fa01]" />
                <span className="text-[11px] font-bold uppercase tracking-wider text-neutral-500 dark:text-neutral-400">
                  Control Operacional del Agente
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-lime-100 text-lime-800 dark:bg-lime-950 dark:text-lime-300 font-medium">
                  Sincronizado con Landing firbyai.com
                </span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-neutral-950 dark:text-white">
                Centro de Control del Agente & Conocimiento
              </h1>
              <p className="text-xs sm:text-sm text-neutral-600 dark:text-neutral-400 mt-1 max-w-3xl">
                Personaliza en caliente los 5 arquetipos de empleados digitales, ajusta las directivas de voz y conducta,
                explora la memoria persistente FTS5, orquesta campañas de reactivación y vincula credenciales de APIs de forma segura.
              </p>
            </div>

            <div className="flex items-center gap-3 shrink-0">
              <div className="text-right">
                <div className="text-[11px] text-neutral-400 uppercase font-semibold">Propietario</div>
                <div className="text-sm font-semibold text-neutral-900 dark:text-neutral-100">Santiago Rubio Parra</div>
                <div className="text-xs text-neutral-500">Growsantix</div>
              </div>
              <div className="h-10 w-10 rounded-full bg-[#b9fa01] text-black font-bold flex items-center justify-center text-sm shadow-xs">
                SR
              </div>
            </div>
          </div>

          {/* NOTIFICATION BANNER */}
          {statusMessage && (
            <div className={`mt-6 p-4 rounded-xl flex items-center gap-3 text-xs font-medium border ${
              statusMessage.type === "error"
                ? "bg-red-50 text-red-700 border-red-200 dark:bg-red-950/40 dark:text-red-300 dark:border-red-900"
                : "bg-lime-50 text-lime-900 border-lime-200 dark:bg-lime-950/40 dark:text-lime-300 dark:border-lime-900"
            }`}>
              {statusMessage.type === "error" ? <AlertCircle className="size-4 shrink-0" /> : <CheckCircle2 className="size-4 shrink-0" />}
              <span>{statusMessage.text}</span>
            </div>
          )}

          {/* NAVEGACIÓN DE PESTAÑAS */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 mt-8 pt-6 border-t border-neutral-100 dark:border-neutral-800">
            <button
              onClick={() => setActiveTab("roles")}
              className={`flex items-center justify-center gap-2 py-3 px-3 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                activeTab === "roles"
                  ? "bg-neutral-900 text-white dark:bg-white dark:text-black shadow-xs"
                  : "bg-neutral-50 dark:bg-neutral-800/60 text-neutral-600 dark:text-neutral-400 hover:text-black dark:hover:text-white"
              }`}
            >
              <Users className="size-4" />
              <span>Arquetipos</span>
            </button>

            <button
              onClick={() => setActiveTab("prompt")}
              className={`flex items-center justify-center gap-2 py-3 px-3 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                activeTab === "prompt"
                  ? "bg-neutral-900 text-white dark:bg-white dark:text-black shadow-xs"
                  : "bg-neutral-50 dark:bg-neutral-800/60 text-neutral-600 dark:text-neutral-400 hover:text-black dark:hover:text-white"
              }`}
            >
              <Sliders className="size-4" />
              <span>Directivas & Tono</span>
            </button>

            <button
              onClick={() => setActiveTab("memory")}
              className={`flex items-center justify-center gap-2 py-3 px-3 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                activeTab === "memory"
                  ? "bg-neutral-900 text-white dark:bg-white dark:text-black shadow-xs"
                  : "bg-neutral-50 dark:bg-neutral-800/60 text-neutral-600 dark:text-neutral-400 hover:text-black dark:hover:text-white"
              }`}
            >
              <Database className="size-4" />
              <span>Memoria FTS5</span>
            </button>

            <button
              onClick={() => setActiveTab("growth")}
              className={`flex items-center justify-center gap-2 py-3 px-3 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                activeTab === "growth"
                  ? "bg-neutral-900 text-white dark:bg-white dark:text-black shadow-xs"
                  : "bg-neutral-50 dark:bg-neutral-800/60 text-neutral-600 dark:text-neutral-400 hover:text-black dark:hover:text-white"
              }`}
            >
              <TrendingUp className="size-4" />
              <span>Growth & Leads</span>
            </button>

            <button
              onClick={() => setActiveTab("vault")}
              className={`flex items-center justify-center gap-2 py-3 px-3 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                activeTab === "vault"
                  ? "bg-neutral-900 text-white dark:bg-white dark:text-black shadow-xs"
                  : "bg-neutral-50 dark:bg-neutral-800/60 text-neutral-600 dark:text-neutral-400 hover:text-black dark:hover:text-white"
              }`}
            >
              <Key className="size-4" />
              <span>Bóveda de APIs</span>
            </button>

            <button
              onClick={() => setActiveTab("voice")}
              className={`flex items-center justify-center gap-2 py-3 px-3 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                activeTab === "voice"
                  ? "bg-neutral-900 text-white dark:bg-white dark:text-black shadow-xs"
                  : "bg-neutral-50 dark:bg-neutral-800/60 text-neutral-600 dark:text-neutral-400 hover:text-black dark:hover:text-white"
              }`}
            >
              <Volume2 className="size-4" />
              <span>Auditor de Voz</span>
            </button>
          </div>
        </div>

        {/* TAB 1: ARQUETIPOS DE EMPLEADOS DIGITALES */}
        {activeTab === "roles" && (
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-bold text-neutral-900 dark:text-white">
                  5 Arquetipos de Empleados Digitales Disponibles
                </h2>
                <p className="text-xs text-neutral-500 dark:text-neutral-400">
                  Selecciona la personalidad y especialidad operativa con la que Firby interactuará en tu sitio web.
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-neutral-500">Rol Activo:</span>
                <span className="px-3 py-1 bg-[#b9fa01] text-black font-bold text-xs rounded-full uppercase tracking-wider">
                  {roles.find(r => r.id === activeRole)?.title || activeRole}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {roles.map((role) => {
                const isActive = role.id === activeRole;
                return (
                  <div
                    key={role.id}
                    className={`relative rounded-2xl p-6 border transition-all flex flex-col justify-between ${
                      isActive
                        ? "bg-white dark:bg-neutral-900 border-[#b9fa01] ring-2 ring-[#b9fa01]/20 shadow-md"
                        : "bg-white dark:bg-neutral-900 border-neutral-200 dark:border-neutral-800 hover:border-neutral-300 dark:hover:border-neutral-700 shadow-2xs"
                    }`}
                  >
                    <div className="space-y-4">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <div className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider">
                            Arquetipo {role.default_name}
                          </div>
                          <h3 className="text-base font-bold text-neutral-900 dark:text-white mt-0.5">
                            {role.title}
                          </h3>
                        </div>
                        {isActive ? (
                          <span className="px-2.5 py-1 rounded-full bg-lime-100 text-lime-800 dark:bg-lime-950 dark:text-lime-300 font-semibold text-[10px] flex items-center gap-1">
                            <CheckCircle2 className="size-3" /> Activo
                          </span>
                        ) : (
                          <span className="px-2.5 py-1 rounded-full bg-neutral-100 text-neutral-600 dark:bg-neutral-800 dark:text-neutral-400 font-medium text-[10px]">
                            Disponible
                          </span>
                        )}
                      </div>

                      <p className="text-xs text-neutral-600 dark:text-neutral-300 leading-relaxed">
                        {role.description}
                      </p>

                      <div className="space-y-2 pt-2">
                        <div className="text-[10px] font-bold text-neutral-400 uppercase tracking-wider">
                          Habilidades Operativas
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          {role.skills.map((skill, idx) => (
                            <span
                              key={idx}
                              className="text-[10px] px-2 py-0.5 rounded-md bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 font-mono"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>

                    <div className="pt-6 mt-6 border-t border-neutral-100 dark:border-neutral-800">
                      <Button
                        onClick={() => handleSelectRole(role.id)}
                        disabled={isActive || updatingRole}
                        className={`w-full py-2.5 rounded-xl font-semibold text-xs cursor-pointer ${
                          isActive
                            ? "bg-neutral-100 dark:bg-neutral-800 text-neutral-400 cursor-default"
                            : "bg-[#b9fa01] hover:bg-[#a6e000] text-black shadow-xs"
                        }`}
                      >
                        {isActive ? "Arquetipo en Operación" : "Activar Este Arquetipo"}
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* TAB 2: DIRECTIVAS Y TONO */}
        {activeTab === "prompt" && (
          <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-2xl p-6 sm:p-8 space-y-6 shadow-2xs">
            <div>
              <h2 className="text-lg font-bold text-neutral-900 dark:text-white">
                Directivas Personalizadas de Conducta y Tono
              </h2>
              <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1">
                Añade instrucciones operativas específicas del negocio. Estas directivas se inyectan dinámicamente en el prompt modular de Sierra AI en caliente sin reiniciar el servidor.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-xs font-semibold text-neutral-700 dark:text-neutral-300">
                  Nombre Público del Agente
                </label>
                <input
                  type="text"
                  value={agentName}
                  onChange={(e) => setAgentName(e.target.value)}
                  placeholder="Firby"
                  className="w-full p-3 rounded-xl bg-neutral-50 dark:bg-neutral-800/60 border border-neutral-200 dark:border-neutral-700 text-xs text-neutral-900 dark:text-white focus:outline-hidden focus:ring-1 focus:ring-lime-500"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-semibold text-neutral-700 dark:text-neutral-300">
                  Cadencia y Dialecto Regional de Voz
                </label>
                <select
                  value={voiceAccent}
                  onChange={(e) => setVoiceAccent(e.target.value)}
                  className="w-full p-3 rounded-xl bg-neutral-50 dark:bg-neutral-800/60 border border-neutral-200 dark:border-neutral-700 text-xs text-neutral-900 dark:text-white focus:outline-hidden focus:ring-1 focus:ring-lime-500"
                >
                  <option value="general">Español Neutro Internacional (Ejecutivo / Directo)</option>
                  <option value="paisa">Español Paisa / Medellín (Cálido, respetuoso y servicial)</option>
                  <option value="argentino">Español Argentino / Rioplatense (Mirá, tenés, claro)</option>
                  <option value="mexicano">Español Mexicano (Cordial, fluido y profesional)</option>
                </select>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-neutral-700 dark:text-neutral-300">
                  Instrucciones Particulares del Negocio (System Prompt Extension)
                </label>
                <span className="text-[11px] text-neutral-400">{systemPrompt.length} caracteres</span>
              </div>
              <textarea
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                placeholder="Ejemplo: Prioriza siempre agendar citas de valoración médica presencial. Si preguntan por financiamiento, aclara que tenemos convenios con Addi y Sistecrédito. Mantén siempre un trato respetuoso y directo..."
                rows={8}
                className="w-full p-4 rounded-xl bg-neutral-50 dark:bg-neutral-800/60 border border-neutral-200 dark:border-neutral-700 text-xs text-neutral-900 dark:text-white placeholder-neutral-400 focus:outline-hidden focus:ring-1 focus:ring-lime-500 leading-relaxed font-sans"
              />
            </div>

            <div className="space-y-3">
              <label className="text-xs font-semibold text-neutral-700 dark:text-neutral-300">
                Límites Operacionales Activos (Barreras Éticas)
              </label>
              <div className="space-y-2">
                {operationalLimits.map((limit, idx) => (
                  <div
                    key={idx}
                    className="flex items-center gap-3 p-3 rounded-xl bg-neutral-50 dark:bg-neutral-800/40 border border-neutral-200 dark:border-neutral-800 text-xs text-neutral-700 dark:text-neutral-300"
                  >
                    <Shield className="size-4 text-lime-500 shrink-0" />
                    <span>{limit}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-4 flex justify-end">
              <Button
                onClick={handleSaveConfig}
                disabled={savingConfig}
                className="bg-neutral-900 hover:bg-neutral-800 text-white dark:bg-white dark:hover:bg-neutral-200 dark:text-black font-semibold text-xs px-6 py-3 rounded-xl shadow-xs cursor-pointer"
              >
                {savingConfig ? "Guardando en Caliente..." : "Guardar Directivas en Caliente"}
              </Button>
            </div>
          </div>
        )}

        {/* TAB 3: MEMORIA PERSISTENTE FTS5 */}
        {activeTab === "memory" && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-2xl p-5 shadow-2xs">
                <div className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider">
                  Mensajes Indexados
                </div>
                <div className="text-2xl font-bold text-neutral-900 dark:text-white mt-1">
                  {memoryStats?.total_msgs || 0}
                </div>
                <div className="text-[10px] text-neutral-500 mt-1">Full-Text Search FTS5 Virtual Table</div>
              </div>

              <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-2xl p-5 shadow-2xs">
                <div className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider">
                  Sesiones Registradas
                </div>
                <div className="text-2xl font-bold text-neutral-900 dark:text-white mt-1">
                  {memoryStats?.total_sess || 0}
                </div>
                <div className="text-[10px] text-neutral-500 mt-1">Historial persistente de clientes</div>
              </div>

              <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-2xl p-5 shadow-2xs">
                <div className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider">
                  Motor de Indexación
                </div>
                <div className="text-base font-bold text-neutral-900 dark:text-white mt-2 flex items-center gap-1.5">
                  <Database className="size-4 text-lime-500" /> Hermes BM25 FTS5
                </div>
                <div className="text-[10px] text-neutral-500 mt-1">SQLite WAL con ranking probabilístico</div>
              </div>
            </div>

            {/* BUSCADOR FTS5 */}
            <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-2xl p-6 sm:p-8 space-y-6 shadow-2xs">
              <div>
                <h3 className="text-base font-bold text-neutral-900 dark:text-white">
                  Búsqueda de Texto Completo en Memoria (BM25)
                </h3>
                <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-0.5">
                  Consulta de forma instantánea cualquier consulta, preferencia de cliente o dato histórico indexado.
                </p>
              </div>

              <div className="flex gap-3">
                <input
                  type="text"
                  value={memoryQuery}
                  onChange={(e) => setMemoryQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSearchMemory()}
                  placeholder="Escribe términos a buscar: 'plan pro', 'horarios', 'precios', 'citas'..."
                  className="flex-1 p-3 rounded-xl bg-neutral-50 dark:bg-neutral-800/60 border border-neutral-200 dark:border-neutral-700 text-xs text-neutral-900 dark:text-white focus:outline-hidden focus:ring-1 focus:ring-lime-500"
                />
                <Button
                  onClick={handleSearchMemory}
                  disabled={searchingMemory}
                  className="bg-[#b9fa01] hover:bg-[#a6e000] text-black font-semibold text-xs px-5 rounded-xl cursor-pointer"
                >
                  {searchingMemory ? <RefreshCw className="size-4 animate-spin" /> : <Search className="size-4" />}
                  <span className="ml-1.5 hidden sm:inline">Buscar en FTS5</span>
                </Button>
              </div>

              {/* RESULTADOS FTS5 */}
              {memoryResults.length > 0 && (
                <div className="space-y-3 pt-2">
                  <div className="text-xs font-semibold text-neutral-500">
                    {memoryResults.length} resultados encontrados ordenados por relevancia BM25:
                  </div>
                  <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
                    {memoryResults.map((item) => (
                      <div
                        key={item.id}
                        className="p-3.5 rounded-xl bg-neutral-50 dark:bg-neutral-800/50 border border-neutral-200 dark:border-neutral-800 text-xs space-y-1"
                      >
                        <div className="flex items-center justify-between text-[10px] text-neutral-400">
                          <span className="font-mono uppercase font-bold text-neutral-600 dark:text-neutral-300">
                            Rol: {item.role}
                          </span>
                          <span>Relevancia: {item.rank?.toFixed(3)}</span>
                        </div>
                        <p className="text-neutral-800 dark:text-neutral-200 leading-relaxed">{item.content}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* AÑADIR HECHO A MEMORIA */}
              <div className="pt-6 border-t border-neutral-100 dark:border-neutral-800 space-y-3">
                <h4 className="text-xs font-bold text-neutral-800 dark:text-neutral-200 uppercase tracking-wider">
                  Indexar Hecho Duradero Manual
                </h4>
                <div className="flex flex-col sm:flex-row gap-3">
                  <input
                    type="text"
                    value={newMemoryContent}
                    onChange={(e) => setNewMemoryContent(e.target.value)}
                    placeholder="Ejemplo: Para pagos internacionales aceptamos PayPal y Stripe con facturación electrónica..."
                    className="flex-1 p-3 rounded-xl bg-neutral-50 dark:bg-neutral-800/60 border border-neutral-200 dark:border-neutral-700 text-xs text-neutral-900 dark:text-white focus:outline-hidden focus:ring-1 focus:ring-lime-500"
                  />
                  <Button
                    onClick={handleAddMemory}
                    disabled={addingMemory || !newMemoryContent.trim()}
                    className="bg-neutral-900 hover:bg-neutral-800 text-white dark:bg-white dark:text-black font-semibold text-xs px-5 py-3 rounded-xl cursor-pointer shrink-0"
                  >
                    {addingMemory ? "Guardando..." : "Guardar en FTS5"}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: MOTOR DE GROWTH Y REACTIVACIÓN */}
        {activeTab === "growth" && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-2xl p-6 sm:p-8 space-y-6 shadow-2xs">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h2 className="text-lg font-bold text-neutral-900 dark:text-white">
                    Motor de Growth & Reactivación de Leads Inactivos
                  </h2>
                  <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1">
                    Detecta contactos que llevan más de 30 o 60 días sin actividad y prepara mensajes hiperpersonalizados con cadencia humana anti-baneo.
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium text-neutral-500">Inactividad:</span>
                  <select
                    value={inactivityDays}
                    onChange={(e) => {
                      const d = Number(e.target.value);
                      setInactivityDays(d);
                      fetchLeads(d);
                    }}
                    className="p-2 rounded-xl bg-neutral-100 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 text-xs text-neutral-900 dark:text-white font-semibold cursor-pointer"
                  >
                    <option value={15}>+15 días</option>
                    <option value={30}>+30 días</option>
                    <option value={60}>+60 días</option>
                    <option value={90}>+90 días</option>
                  </select>
                </div>
              </div>

              {/* LISTA DE LEADS INACTIVOS */}
              <div className="border border-neutral-100 dark:border-neutral-800 rounded-xl overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-neutral-50 dark:bg-neutral-800/60 text-neutral-500 font-semibold border-b border-neutral-200 dark:border-neutral-800">
                    <tr>
                      <th className="p-3">Nombre</th>
                      <th className="p-3">Teléfono / Chat ID</th>
                      <th className="p-3">Último Servicio</th>
                      <th className="p-3">Última Fecha</th>
                      <th className="p-3">Estado</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-neutral-100 dark:divide-neutral-800">
                    {loadingLeads ? (
                      <tr>
                        <td colSpan={5} className="p-6 text-center text-neutral-400">
                          Cargando leads inactivos...
                        </td>
                      </tr>
                    ) : leads.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="p-6 text-center text-neutral-400">
                          No hay leads que coincidan con el filtro de inactividad seleccionado.
                        </td>
                      </tr>
                    ) : (
                      leads.slice(0, 8).map((lead) => (
                        <tr key={lead.id} className="hover:bg-neutral-50/50 dark:hover:bg-neutral-800/30">
                          <td className="p-3 font-semibold text-neutral-900 dark:text-white">{lead.name}</td>
                          <td className="p-3 font-mono text-[11px] text-neutral-500">{lead.phone || lead.chat_id}</td>
                          <td className="p-3 text-neutral-700 dark:text-neutral-300">{lead.last_service}</td>
                          <td className="p-3 text-neutral-500">{lead.last_seen || "Sin registro"}</td>
                          <td className="p-3">
                            <span className="px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 font-semibold text-[10px]">
                              Inactivo ({inactivityDays}d+)
                            </span>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>

              {/* GENERADOR DE CAMPAÑA */}
              <div className="pt-6 border-t border-neutral-100 dark:border-neutral-800 space-y-4">
                <h3 className="text-sm font-bold text-neutral-900 dark:text-white">
                  Simulador de Campaña con Intervalos Anti-Baneo
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-neutral-700 dark:text-neutral-300">
                      Servicio o Motivo de Seguimiento
                    </label>
                    <input
                      type="text"
                      value={campaignServiceName}
                      onChange={(e) => setCampaignServiceName(e.target.value)}
                      className="w-full p-2.5 rounded-xl bg-neutral-50 dark:bg-neutral-800/60 border border-neutral-200 dark:border-neutral-700 text-xs text-neutral-900 dark:text-white"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-neutral-700 dark:text-neutral-300">
                      Beneficio o Propuesta de Valor
                    </label>
                    <input
                      type="text"
                      value={campaignOffer}
                      onChange={(e) => setCampaignOffer(e.target.value)}
                      className="w-full p-2.5 rounded-xl bg-neutral-50 dark:bg-neutral-800/60 border border-neutral-200 dark:border-neutral-700 text-xs text-neutral-900 dark:text-white"
                    />
                  </div>
                </div>

                <div className="flex justify-end">
                  <Button
                    onClick={handleGenerateCampaignPreview}
                    disabled={generatingCampaign}
                    className="bg-[#b9fa01] hover:bg-[#a6e000] text-black font-semibold text-xs px-5 py-2.5 rounded-xl cursor-pointer"
                  >
                    {generatingCampaign ? "Generando Simulación..." : "Previsualizar Campaña Proactiva"}
                  </Button>
                </div>

                {campaignPreviews.length > 0 && (
                  <div className="space-y-3 pt-4">
                    <div className="text-xs font-semibold text-neutral-500">
                      Vistas previas de mensajes con espaciado humano simulado:
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {campaignPreviews.map((p, idx) => (
                        <div
                          key={idx}
                          className="p-4 rounded-xl bg-neutral-50 dark:bg-neutral-800/40 border border-neutral-200 dark:border-neutral-700 space-y-2 text-xs"
                        >
                          <div className="flex items-center justify-between text-[11px]">
                            <span className="font-bold text-neutral-900 dark:text-white">{p.recipient_name}</span>
                            <span className="text-neutral-400 font-mono">Retraso: {p.simulated_cadence_seconds}s</span>
                          </div>
                          <p className="text-neutral-700 dark:text-neutral-300 leading-relaxed italic bg-white dark:bg-neutral-900 p-3 rounded-lg border border-neutral-100 dark:border-neutral-800">
                            "{p.message}"
                          </p>
                          <div className="text-[10px] font-semibold text-lime-600 dark:text-lime-400 flex items-center gap-1">
                            <CheckCircle2 className="size-3" /> {p.anti_ban_status}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB 5: BÓVEDA DE CREDENCIALES Y HTTP EXECUTOR */}
        {activeTab === "vault" && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-2xl p-6 sm:p-8 space-y-6 shadow-2xs">
              <div>
                <h2 className="text-lg font-bold text-neutral-900 dark:text-white">
                  Bóveda de Credenciales y Ejecutor HTTP Autónomo
                </h2>
                <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1">
                  Guarda de forma encriptada las llaves de tus servicios externos. Firby las inyectará automáticamente en encabezados de autorización sin exponer los secretos.
                </p>
              </div>

              {/* ESTADO DE CONEXIONES */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {vaultIntegrations.map((item) => (
                  <div
                    key={item.id}
                    className="p-4 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-800/40 space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-bold text-neutral-900 dark:text-white">{item.name}</h4>
                      {item.is_configured ? (
                        <span className="px-2 py-0.5 rounded-full bg-lime-100 text-lime-800 dark:bg-lime-950 dark:text-lime-300 font-semibold text-[10px]">
                          Conectado
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded-full bg-neutral-200 text-neutral-600 dark:bg-neutral-700 dark:text-neutral-400 font-medium text-[10px]">
                          No configurado
                        </span>
                      )}
                    </div>
                    <div className="text-[11px] text-neutral-500">{item.category}</div>
                    {item.masked_token && (
                      <div className="font-mono text-[10px] text-neutral-400">Token: {item.masked_token}</div>
                    )}
                  </div>
                ))}
              </div>

              {/* FORMULARIO DE GUARDADO DE LLAVE */}
              <div className="pt-6 border-t border-neutral-100 dark:border-neutral-800 space-y-4">
                <h3 className="text-sm font-bold text-neutral-900 dark:text-white">
                  Vincular o Actualizar Llave de API en la Bóveda
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-neutral-700 dark:text-neutral-300">Servicio</label>
                    <select
                      value={selectedService}
                      onChange={(e) => setSelectedService(e.target.value)}
                      className="w-full p-2.5 rounded-xl bg-neutral-50 dark:bg-neutral-800/60 border border-neutral-200 dark:border-neutral-700 text-xs text-neutral-900 dark:text-white"
                    >
                      <option value="notion">Notion API</option>
                      <option value="google_sheets">Google Sheets</option>
                      <option value="google_calendar">Google Calendar</option>
                      <option value="hubspot">HubSpot CRM</option>
                      <option value="custom_webhook">Webhook Personalizado</option>
                    </select>
                  </div>

                  <div className="sm:col-span-2 space-y-1.5">
                    <label className="text-xs font-semibold text-neutral-700 dark:text-neutral-300">
                      Token Secreto o Llave API
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="password"
                        value={apiKeyInput}
                        onChange={(e) => setApiKeyInput(e.target.value)}
                        placeholder="secret_... o token..."
                        className="flex-1 p-2.5 rounded-xl bg-neutral-50 dark:bg-neutral-800/60 border border-neutral-200 dark:border-neutral-700 text-xs text-neutral-900 dark:text-white font-mono"
                      />
                      <Button
                        onClick={handleSaveVaultKey}
                        disabled={savingKey || !apiKeyInput.trim()}
                        className="bg-neutral-900 hover:bg-neutral-800 text-white dark:bg-white dark:text-black font-semibold text-xs px-4 rounded-xl cursor-pointer"
                      >
                        {savingKey ? "Guardando..." : "Guardar Llave"}
                      </Button>
                    </div>
                  </div>
                </div>
              </div>

              {/* TESTER HTTP EXECUTOR CON SSRF SHIELD */}
              <div className="pt-6 border-t border-neutral-100 dark:border-neutral-800 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-neutral-900 dark:text-white flex items-center gap-2">
                    <Shield className="size-4 text-lime-500" />
                    Ejecutor de Pruebas HTTP (Blindaje SSRF Activado)
                  </h3>
                  <span className="text-[10px] text-neutral-400">Hermes HTTP Tool Standard</span>
                </div>

                <div className="flex flex-col sm:flex-row gap-3">
                  <select
                    value={testMethod}
                    onChange={(e) => setTestMethod(e.target.value)}
                    className="p-2.5 rounded-xl bg-neutral-50 dark:bg-neutral-800/60 border border-neutral-200 dark:border-neutral-700 text-xs font-bold text-neutral-900 dark:text-white w-24 shrink-0"
                  >
                    <option value="GET">GET</option>
                    <option value="POST">POST</option>
                  </select>
                  <input
                    type="text"
                    value={testUrl}
                    onChange={(e) => setTestUrl(e.target.value)}
                    placeholder="https://api.notion.com/v1/..."
                    className="flex-1 p-2.5 rounded-xl bg-neutral-50 dark:bg-neutral-800/60 border border-neutral-200 dark:border-neutral-700 text-xs text-neutral-900 dark:text-white font-mono"
                  />
                  <Button
                    onClick={handleExecuteHttpTest}
                    disabled={executingTest}
                    className="bg-[#b9fa01] hover:bg-[#a6e000] text-black font-semibold text-xs px-5 rounded-xl cursor-pointer shrink-0"
                  >
                    {executingTest ? "Ejecutando..." : "Probar Llamada"}
                  </Button>
                </div>

                {testResult && (
                  <div className="p-4 rounded-xl bg-neutral-950 text-neutral-200 font-mono text-[11px] space-y-2 border border-neutral-800 overflow-x-auto">
                    <div className="flex items-center justify-between text-neutral-400">
                      <span>Resultado de la petición:</span>
                      <span className={testResult.success ? "text-lime-400 font-bold" : "text-red-400 font-bold"}>
                        Status: {testResult.status_code || "Error"}
                      </span>
                    </div>
                    <pre className="text-[10px] text-neutral-300 max-h-48 overflow-y-auto">
                      {JSON.stringify(testResult, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB 6: AUDITOR DE VOZ Y GUIONES */}
        {activeTab === "voice" && (
          <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-2xl p-6 sm:p-8 space-y-6 shadow-2xs">
            <div>
              <h2 className="text-lg font-bold text-neutral-900 dark:text-white">
                Auditor Fonético de Guiones (Firby Audio Auditor)
              </h2>
              <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1">
                Refina textos antes de enviarlos a síntesis de voz TTS. Inserta pausas naturales, elimina rigidez sintética y calibra la cadencia según el dialecto regional seleccionado.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-2">
                <label className="text-xs font-semibold text-neutral-700 dark:text-neutral-300">
                  Región / Dialecto Fonético
                </label>
                <select
                  value={auditorAccent}
                  onChange={(e) => setAuditorAccent(e.target.value)}
                  className="w-full p-3 rounded-xl bg-neutral-50 dark:bg-neutral-800/60 border border-neutral-200 dark:border-neutral-700 text-xs text-neutral-900 dark:text-white"
                >
                  <option value="paisa">Paisa (Colombia) - Muletillas: Vea pues, claro, te cuento...</option>
                  <option value="argentino">Argentino (Rioplatense) - Muletillas: Che, mirá, viste...</option>
                  <option value="mexicano">Mexicano - Muletillas: Oye, miren, claro que sí...</option>
                  <option value="general">Español General - Pausas sutiles balanceadas</option>
                </select>
              </div>

              <div className="md:col-span-2 space-y-2">
                <label className="text-xs font-semibold text-neutral-700 dark:text-neutral-300">
                  Texto o Guion de Prueba
                </label>
                <textarea
                  value={audioScript}
                  onChange={(e) => setAudioScript(e.target.value)}
                  rows={3}
                  className="w-full p-3 rounded-xl bg-neutral-50 dark:bg-neutral-800/60 border border-neutral-200 dark:border-neutral-700 text-xs text-neutral-900 dark:text-white leading-relaxed"
                />
              </div>
            </div>

            <div className="flex justify-end">
              <Button
                onClick={handleAuditAudio}
                disabled={auditingAudio || !audioScript.trim()}
                className="bg-[#b9fa01] hover:bg-[#a6e000] text-black font-semibold text-xs px-6 py-2.5 rounded-xl cursor-pointer"
              >
                {auditingAudio ? "Auditor Evaluando..." : "Auditar y Refinar Guion"}
              </Button>
            </div>

            {auditedScript && (
              <div className="mt-6 p-5 rounded-2xl bg-neutral-50 dark:bg-neutral-800/50 border border-neutral-200 dark:border-neutral-800 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-neutral-900 dark:text-white">Guion Fonético Refinado:</span>
                    <span className="px-2 py-0.5 rounded-full bg-lime-100 text-lime-800 dark:bg-lime-950 dark:text-lime-300 text-[10px] font-bold">
                      Naturalidad: {auditedScript.naturalness_score}
                    </span>
                  </div>
                  <span className="text-[11px] text-neutral-400 uppercase font-mono">Región: {auditedScript.accent}</span>
                </div>

                <div className="p-4 rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 text-xs text-neutral-900 dark:text-white leading-relaxed font-sans">
                  "{auditedScript.refined_script}"
                </div>

                <div className="space-y-1.5 pt-1">
                  <div className="text-[10px] font-bold text-neutral-400 uppercase tracking-wider">
                    Mejoras Aplicadas por el Auditor
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {auditedScript.improvements?.map((imp: string, i: number) => (
                      <span
                        key={i}
                        className="text-[11px] px-2.5 py-1 rounded-lg bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 flex items-center gap-1.5"
                      >
                        <CheckCircle2 className="size-3 text-lime-500" /> {imp}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}
