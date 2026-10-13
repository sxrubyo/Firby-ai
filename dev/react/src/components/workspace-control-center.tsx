"use client";

import React, { useState, useEffect, useCallback } from "react";
import { playSound } from "@/lib/sound";
import {
  Activity,
  AlertOctagon,
  AlertTriangle,
  ArrowRight,
  BookOpen,
  Calendar,
  Check,
  CheckCircle2,
  ChevronRight,
  Clock,
  Code2,
  Copy,
  CreditCard,
  ExternalLink,
  Flame,
  GitBranch,
  Globe,
  Layers,
  MessageSquare,
  PauseCircle,
  PlayCircle,
  Plus,
  Power,
  RefreshCw,
  Search,
  Send,
  Settings,
  Shield,
  Sliders,
  Trash2,
  UserCheck,
  Users,
  Wrench,
  X,
  XCircle,
  Zap,
} from "lucide-react";

// Types
type TabType =
  | "overview"
  | "runs"
  | "conversations"
  | "knowledge"
  | "rules"
  | "tools"
  | "workflows"
  | "integrations"
  | "billing"
  | "onboarding";

interface OverviewData {
  agent: {
    agent_id: string;
    tenant_id: string;
    name: string;
    operational_state: "ONLINE" | "PAUSED" | "MAINTENANCE" | "ERROR";
    published_version: string;
    runtime_version: string;
  };
  metrics: {
    total_conversations: number;
    today_conversations: number;
    confirmed_appointments: number;
    tasks_completed: number;
    pending_approvals: number;
    knowledge_items: number;
    active_rules: number;
    active_workflows: number;
  };
  billing: {
    plan_name: string;
    price_cop: string;
    trial_active: boolean;
    trial_status: string;
    days_remaining: number;
    next_billing_date: string;
    can_cancel: boolean;
    cancel_policy: string;
  };
  recent_activity: Array<{
    event_id: string;
    action: string;
    actor: string;
    timestamp: string;
    details: any;
  }>;
}

export function WorkspaceControlCenter() {
  const [activeTab, setActiveTab] = useState<TabType>("overview");
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" | "info" } | null>(null);

  // Modal states
  const [killSwitchModalOpen, setKillSwitchModalOpen] = useState(false);
  const [cancelBillingModalOpen, setCancelBillingModalOpen] = useState(false);
  const [copiedSnippet, setCopiedSnippet] = useState(false);

  // Runs tab state
  const [runs, setRuns] = useState<any[]>([]);
  const [runsFilter, setRunsFilter] = useState<string>("all");

  // Conversations tab state
  const [conversations, setConversations] = useState<any[]>([]);
  const [selectedChat, setSelectedChat] = useState<any | null>(null);
  const [chatDetail, setChatDetail] = useState<any | null>(null);

  // Knowledge tab state
  const [knowledgeList, setKnowledgeList] = useState<any[]>([]);
  const [newTitle, setNewTitle] = useState("");
  const [newContent, setNewContent] = useState("");
  const [newCategory, setNewCategory] = useState("business");
  const [teachInstruction, setTeachInstruction] = useState("");
  const [isTeaching, setIsTeaching] = useState(false);

  // Rules tab state
  const [rules, setRules] = useState<any[]>([]);
  const [newCondition, setNewCondition] = useState("");
  const [newDirective, setNewDirective] = useState("");
  const [newRuleCategory, setNewRuleCategory] = useState("policy");

  // Tools tab state
  const [tools, setTools] = useState<any[]>([]);

  // Workflows tab state
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<any | null>(null);
  const [dryRunPayload, setDryRunPayload] = useState(
    JSON.stringify(
      {
        customer_name: "Laura Gómez",
        phone: "+57 300 123 4567",
        service: "Consulta de Valoración",
        discount_pct: 20,
      },
      null,
      2
    )
  );
  const [dryRunResult, setDryRunResult] = useState<any | null>(null);
  const [isDryRunning, setIsDryRunning] = useState(false);

  // Integrations tab state
  const [integrations, setIntegrations] = useState<any[]>([]);
  const [waPhoneNumberId, setWaPhoneNumberId] = useState("");
  const [waBusinessAccountId, setWaBusinessAccountId] = useState("");
  const [waAccessToken, setWaAccessToken] = useState("");

  // Onboarding tab state
  const [onboarding, setOnboarding] = useState<any | null>(null);

  const showToast = useCallback((message: string, type: "success" | "error" | "info" = "success") => {
    setToast({ message, type });
    playSound("pop");
    setTimeout(() => setToast(null), 4000);
  }, []);

  // Fetch Overview Data
  const fetchOverview = useCallback(async () => {
    try {
      const res = await fetch("/api/workspace/overview");
      if (res.ok) {
        const data = await res.json();
        setOverview(data);
      }
    } catch (err) {
      console.error("Error fetching overview:", err);
    }
  }, []);

  // Initial Load
  useEffect(() => {
    const init = async () => {
      setLoading(true);
      await fetchOverview();
      setLoading(false);
    };
    init();
  }, [fetchOverview]);

  // Tab Data Fetching
  useEffect(() => {
    if (activeTab === "runs") {
      fetch("/api/workspace/runs")
        .then((r) => r.json())
        .then((d) => setRuns(d.runs || []))
        .catch(console.error);
    } else if (activeTab === "conversations") {
      fetch("/api/workspace/conversations")
        .then((r) => r.json())
        .then((d) => setConversations(d.conversations || []))
        .catch(console.error);
    } else if (activeTab === "knowledge") {
      fetch("/api/workspace/knowledge")
        .then((r) => r.json())
        .then((d) => setKnowledgeList(d.knowledge || []))
        .catch(console.error);
    } else if (activeTab === "rules") {
      fetch("/api/workspace/rules")
        .then((r) => r.json())
        .then((d) => setRules(d.rules || []))
        .catch(console.error);
    } else if (activeTab === "tools") {
      fetch("/api/workspace/tools")
        .then((r) => r.json())
        .then((d) => setTools(d.tools || []))
        .catch(console.error);
    } else if (activeTab === "workflows") {
      fetch("/api/workspace/workflows")
        .then((r) => r.json())
        .then((d) => {
          setWorkflows(d.workflows || []);
          if (d.workflows && d.workflows.length > 0 && !selectedWorkflow) {
            setSelectedWorkflow(d.workflows[0]);
          }
        })
        .catch(console.error);
    } else if (activeTab === "integrations") {
      fetch("/api/workspace/integrations")
        .then((r) => r.json())
        .then((d) => setIntegrations(d.integrations || []))
        .catch(console.error);
    } else if (activeTab === "onboarding") {
      fetch("/api/workspace/onboarding")
        .then((r) => r.json())
        .then((d) => setOnboarding(d.onboarding || null))
        .catch(console.error);
    }
  }, [activeTab, selectedWorkflow]);

  // Select conversation detail
  useEffect(() => {
    if (selectedChat) {
      fetch(`/api/workspace/conversations/${encodeURIComponent(selectedChat.chat_id)}`)
        .then((r) => r.json())
        .then((d) => setChatDetail(d.detail || null))
        .catch(console.error);
    }
  }, [selectedChat]);

  // Operational state change
  const handleSetAgentState = async (state: "ONLINE" | "PAUSED" | "MAINTENANCE") => {
    try {
      const res = await fetch("/api/workspace/agent/state", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ state, reason: "Cambio manual por el administrador" }),
      });
      const data = await res.json();
      if (data.ok) {
        showToast(`Agente configurado en modo ${state}`, "success");
        await fetchOverview();
      } else {
        showToast(data.error || "No se pudo cambiar el estado", "error");
      }
    } catch (err) {
      showToast("Error de comunicación con el servidor", "error");
    }
  };

  // Emergency Stop Kill Switch
  const handleEmergencyStop = async () => {
    try {
      const res = await fetch("/api/workspace/agent/emergency-stop", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ actor: "admin" }),
      });
      const data = await res.json();
      if (data.ok) {
        showToast("PARADA DE EMERGENCIA: Agente pausado y ejecuciones activas abortadas", "error");
        setKillSwitchModalOpen(false);
        await fetchOverview();
      } else {
        showToast(data.error || "Error al activar Kill Switch", "error");
      }
    } catch (err) {
      showToast("Error ejecutando parada de emergencia", "error");
    }
  };

  // Run actions (HITL)
  const handleApproveRun = async (runId: string) => {
    try {
      const res = await fetch(`/api/workspace/runs/${runId}/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ actor: "admin" }),
      });
      const data = await res.json();
      if (data.ok) {
        showToast("Acción aprobada exitosamente", "success");
        setRuns((prev) =>
          prev.map((r) => (r.run_id === runId ? { ...r, state: "RUNNING" } : r))
        );
        fetchOverview();
      }
    } catch {
      showToast("Error aprobando la acción", "error");
    }
  };

  const handleDenyRun = async (runId: string) => {
    try {
      const res = await fetch(`/api/workspace/runs/${runId}/deny`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason: "Rechazado por el administrador", actor: "admin" }),
      });
      const data = await res.json();
      if (data.ok) {
        showToast("Acción rechazada", "info");
        setRuns((prev) =>
          prev.map((r) => (r.run_id === runId ? { ...r, state: "RUNNING" } : r))
        );
        fetchOverview();
      }
    } catch {
      showToast("Error rechazando la acción", "error");
    }
  };

  const handleCancelRun = async (runId: string) => {
    try {
      const res = await fetch(`/api/workspace/runs/${runId}/cancel`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason: "Cancelado desde panel de control", actor: "admin" }),
      });
      const data = await res.json();
      if (data.ok) {
        showToast("Ejecución cancelada", "info");
        setRuns((prev) =>
          prev.map((r) => (r.run_id === runId ? { ...r, state: "CANCELLED" } : r))
        );
      }
    } catch {
      showToast("Error cancelando ejecución", "error");
    }
  };

  // Add knowledge
  const handleAddKnowledge = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || !newContent.trim()) return;

    try {
      const res = await fetch("/api/workspace/knowledge", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: newTitle.trim(),
          content: newContent.trim(),
          category: newCategory,
          priority: 0,
        }),
      });
      const data = await res.json();
      if (data.ok) {
        showToast("Documento de conocimiento guardado exitosamente");
        setNewTitle("");
        setNewContent("");
        setKnowledgeList((prev) => [data.item, ...prev]);
        fetchOverview();
      }
    } catch {
      showToast("Error guardando conocimiento", "error");
    }
  };

  // Natural language teaching
  const handleTeachAgent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!teachInstruction.trim() || isTeaching) return;
    setIsTeaching(true);

    try {
      const res = await fetch("/api/workspace/knowledge/teach", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ instruction: teachInstruction.trim(), actor: "admin" }),
      });
      const data = await res.json();
      if (data.ok) {
        showToast(`Conocimiento aprendido: ${data.title}`);
        setTeachInstruction("");
        // Actualizar listas si existen
        if (data.knowledge_item) setKnowledgeList((prev) => [data.knowledge_item, ...prev]);
        if (data.rule) setRules((prev) => [data.rule, ...prev]);
        fetchOverview();
      }
    } catch {
      showToast("Error procesando la enseñanza", "error");
    } finally {
      setIsTeaching(false);
    }
  };

  // Toggle Rule
  const handleToggleRule = async (ruleId: string, currentActive: boolean) => {
    try {
      const res = await fetch(`/api/workspace/rules/${ruleId}/toggle`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_active: !currentActive }),
      });
      const data = await res.json();
      if (data.ok) {
        setRules((prev) =>
          prev.map((r) => (r.id === ruleId || r.rule_id === ruleId ? { ...r, is_active: !currentActive } : r))
        );
        showToast(`Regla ${!currentActive ? "activada" : "desactivada"}`);
        fetchOverview();
      }
    } catch {
      showToast("Error modificando regla", "error");
    }
  };

  // Create rule
  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCondition.trim() || !newDirective.trim()) return;

    try {
      const res = await fetch("/api/workspace/rules", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          trigger_condition: newCondition.trim(),
          directive: newDirective.trim(),
          category: newRuleCategory,
        }),
      });
      const data = await res.json();
      if (data.ok) {
        showToast("Regla estructurada creada exitosamente");
        setNewCondition("");
        setNewDirective("");
        setRules((prev) => [data.rule, ...prev]);
        fetchOverview();
      }
    } catch {
      showToast("Error creando regla", "error");
    }
  };

  // Toggle tool
  const handleToggleTool = async (toolId: string, currentActive: boolean, currentHitl: boolean) => {
    try {
      const res = await fetch(`/api/workspace/tools/${toolId}/permission`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_active: !currentActive, requires_hitl: currentHitl }),
      });
      const data = await res.json();
      if (data.ok) {
        setTools((prev) =>
          prev.map((t) => (t.id === toolId ? { ...t, is_active: !currentActive, enabled: !currentActive } : t))
        );
        showToast(`Capacidad ${!currentActive ? "activada" : "desactivada"}`);
      }
    } catch {
      showToast("Error actualizando capacidad", "error");
    }
  };

  // Toggle tool HITL
  const handleToggleToolHitl = async (toolId: string, currentActive: boolean, currentHitl: boolean) => {
    try {
      const res = await fetch(`/api/workspace/tools/${toolId}/permission`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_active: currentActive, requires_hitl: !currentHitl }),
      });
      const data = await res.json();
      if (data.ok) {
        setTools((prev) =>
          prev.map((t) =>
            t.id === toolId ? { ...t, requires_hitl: !currentHitl, requires_approval: !currentHitl } : t
          )
        );
        showToast(`Supervisión humana ${!currentHitl ? "requerida" : "opcional"}`);
      }
    } catch {
      showToast("Error actualizando nivel de supervisión", "error");
    }
  };

  // Dry-Run Simulator
  const handleRunSimulator = async () => {
    if (!selectedWorkflow) return;
    setIsDryRunning(true);
    setDryRunResult(null);

    try {
      let parsedPayload = {};
      try {
        parsedPayload = JSON.parse(dryRunPayload);
      } catch {
        showToast("El payload de prueba debe ser un JSON válido", "error");
        setIsDryRunning(false);
        return;
      }

      const res = await fetch("/api/workspace/workflows/dry-run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          workflow_id: selectedWorkflow.id || selectedWorkflow.workflow_id,
          payload: parsedPayload,
        }),
      });
      const data = await res.json();
      setDryRunResult(data);
      if (data.ok) {
        showToast("Simulación completada en sandbox sin efectos externos");
      }
    } catch {
      showToast("Error en simulación", "error");
    } finally {
      setIsDryRunning(false);
    }
  };

  // Save Meta WhatsApp
  const handleSaveWhatsApp = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch("/api/workspace/integrations/meta_whatsapp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          config: {
            phone_number_id: waPhoneNumberId.trim(),
            business_account_id: waBusinessAccountId.trim(),
            access_token: waAccessToken.trim(),
            webhook_verified: true,
          },
        }),
      });
      const data = await res.json();
      if (data.ok) {
        showToast("Credenciales de Meta WhatsApp Business guardadas");
        setIntegrations((prev) =>
          prev.map((i) => (i.id === "meta_whatsapp" || i.id === "whatsapp" ? { ...i, connected: true, status: "CONNECTED" } : i))
        );
      }
    } catch {
      showToast("Error guardando credenciales", "error");
    }
  };

  // Cancel Billing in 1 click
  const handleCancelBilling = async () => {
    try {
      const res = await fetch("/api/workspace/billing/cancel", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason: "user_cancelled_from_workspace_ui" }),
      });
      const data = await res.json();
      if (data.ok) {
        showToast("Suscripción cancelada exitosamente. No se generarán cobros.", "info");
        setCancelBillingModalOpen(false);
        await fetchOverview();
      }
    } catch {
      showToast("Error al procesar la cancelación", "error");
    }
  };

  // Complete onboarding step
  const handleCompleteOnboardingStep = async (stepKey: string) => {
    try {
      const res = await fetch("/api/workspace/onboarding/step", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ step_key: stepKey }),
      });
      const data = await res.json();
      if (data.ok) {
        setOnboarding(data);
        showToast("Paso de configuración marcado como completado");
      }
    } catch {
      showToast("Error al avanzar paso", "error");
    }
  };

  const copyScriptSnippet = () => {
    const code = `<script src="https://firbyai.com/firby.js" data-agent="clinica-de-las-americas" async></script>`;
    navigator.clipboard.writeText(code);
    setCopiedSnippet(true);
    setTimeout(() => setCopiedSnippet(false), 2500);
    showToast("Código de instalación copiado al portapapeles");
  };

  const agentState = overview?.agent?.operational_state || "ONLINE";

  return (
    <div className="flex h-screen w-full bg-[#090a0f] text-neutral-100 font-sans antialiased overflow-hidden select-none">
      {/* ─── TOAST NOTIFICATION ─── */}
      {toast && (
        <div
          className={`fixed bottom-6 right-6 z-50 px-4 py-3 rounded-lg border text-sm font-medium shadow-2xl flex items-center gap-3 transition-all ${
            toast.type === "error"
              ? "bg-[#1f0d0d] border-red-900/60 text-red-300"
              : toast.type === "info"
              ? "bg-[#0d1726] border-blue-900/60 text-blue-300"
              : "bg-[#0d1f14] border-emerald-900/60 text-emerald-300"
          }`}
        >
          {toast.type === "error" ? (
            <XCircle className="w-4 h-4 text-red-400 shrink-0" />
          ) : (
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          )}
          <span>{toast.message}</span>
        </div>
      )}

      {/* ─── SIDEBAR DE OPERACIÓN ─── */}
      <aside className="w-64 border-r border-[#191c24] bg-[#0c0e14] flex flex-col justify-between shrink-0 z-20">
        <div>
          {/* Logo & Tenant */}
          <div className="h-16 px-5 border-b border-[#191c24] flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-md bg-[#00F279] flex items-center justify-center font-bold text-black text-xs tracking-wider">
                F
              </div>
              <div className="leading-tight">
                <span className="font-semibold text-sm tracking-tight text-white block">Firby Control</span>
                <span className="text-[10px] text-neutral-400 font-mono block truncate max-w-[130px]">
                  {overview?.agent?.name || "Clínica Las Américas"}
                </span>
              </div>
            </div>
            <span
              className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded border uppercase ${
                agentState === "ONLINE"
                  ? "bg-emerald-950/60 text-emerald-400 border-emerald-800/60"
                  : agentState === "PAUSED"
                  ? "bg-amber-950/60 text-amber-400 border-amber-800/60"
                  : "bg-red-950/60 text-red-400 border-red-800/60"
              }`}
            >
              {agentState}
            </span>
          </div>

          {/* Navigation Items */}
          <nav className="p-3 space-y-1">
            <button
              type="button"
              onClick={() => setActiveTab("overview")}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                activeTab === "overview"
                  ? "bg-[#191d28] text-white"
                  : "text-neutral-400 hover:text-neutral-200 hover:bg-[#12151c]"
              }`}
            >
              <Activity className="w-4 h-4 text-[#00F279]" />
              <span>Vista General</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("runs")}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                activeTab === "runs"
                  ? "bg-[#191d28] text-white"
                  : "text-neutral-400 hover:text-neutral-200 hover:bg-[#12151c]"
              }`}
            >
              <div className="flex items-center gap-3">
                <PlayCircle className="w-4 h-4 text-neutral-400" />
                <span>Ejecuciones & HITL</span>
              </div>
              {overview && overview.metrics.pending_approvals > 0 && (
                <span className="px-1.5 py-0.5 text-[10px] font-mono font-bold rounded bg-amber-500/20 text-amber-400 border border-amber-500/40">
                  {overview.metrics.pending_approvals}
                </span>
              )}
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("conversations")}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                activeTab === "conversations"
                  ? "bg-[#191d28] text-white"
                  : "text-neutral-400 hover:text-neutral-200 hover:bg-[#12151c]"
              }`}
            >
              <MessageSquare className="w-4 h-4 text-neutral-400" />
              <span>Conversaciones</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("knowledge")}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                activeTab === "knowledge"
                  ? "bg-[#191d28] text-white"
                  : "text-neutral-400 hover:text-neutral-200 hover:bg-[#12151c]"
              }`}
            >
              <BookOpen className="w-4 h-4 text-neutral-400" />
              <span>Conocimiento</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("rules")}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                activeTab === "rules"
                  ? "bg-[#191d28] text-white"
                  : "text-neutral-400 hover:text-neutral-200 hover:bg-[#12151c]"
              }`}
            >
              <Shield className="w-4 h-4 text-neutral-400" />
              <span>Reglas de Negocio</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("tools")}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                activeTab === "tools"
                  ? "bg-[#191d28] text-white"
                  : "text-neutral-400 hover:text-neutral-200 hover:bg-[#12151c]"
              }`}
            >
              <Wrench className="w-4 h-4 text-neutral-400" />
              <span>Capacidades / Tools</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("workflows")}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                activeTab === "workflows"
                  ? "bg-[#191d28] text-white"
                  : "text-neutral-400 hover:text-neutral-200 hover:bg-[#12151c]"
              }`}
            >
              <GitBranch className="w-4 h-4 text-neutral-400" />
              <span>Flujos (n8n Engine)</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("integrations")}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                activeTab === "integrations"
                  ? "bg-[#191d28] text-white"
                  : "text-neutral-400 hover:text-neutral-200 hover:bg-[#12151c]"
              }`}
            >
              <Globe className="w-4 h-4 text-neutral-400" />
              <span>Canales & APIs</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("billing")}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                activeTab === "billing"
                  ? "bg-[#191d28] text-white"
                  : "text-neutral-400 hover:text-neutral-200 hover:bg-[#12151c]"
              }`}
            >
              <div className="flex items-center gap-3">
                <CreditCard className="w-4 h-4 text-neutral-400" />
                <span>Facturación & Trial</span>
              </div>
              {overview?.billing?.trial_active && (
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-950/60 text-blue-400 border border-blue-900/60">
                  {overview.billing.days_remaining}d
                </span>
              )}
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("onboarding")}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                activeTab === "onboarding"
                  ? "bg-[#191d28] text-white"
                  : "text-neutral-400 hover:text-neutral-200 hover:bg-[#12151c]"
              }`}
            >
              <CheckCircle2 className="w-4 h-4 text-neutral-400" />
              <span>Setup de 7 Pasos</span>
            </button>
          </nav>
        </div>

        {/* Bottom Agent Controller Card */}
        <div className="p-3 border-t border-[#191c24] space-y-2.5">
          <div className="bg-[#12151e] rounded-md p-2.5 border border-[#202533]">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-[11px] font-medium text-neutral-300">Modo de Operación</span>
              <span className="text-[10px] font-mono text-neutral-400">
                {overview?.agent?.published_version || "v1"}
              </span>
            </div>
            <div className="grid grid-cols-3 gap-1">
              <button
                type="button"
                onClick={() => handleSetAgentState("ONLINE")}
                className={`py-1 text-[10px] font-medium rounded transition-colors ${
                  agentState === "ONLINE"
                    ? "bg-emerald-600 text-white font-semibold"
                    : "bg-[#191d28] text-neutral-400 hover:text-white"
                }`}
              >
                Online
              </button>
              <button
                type="button"
                onClick={() => handleSetAgentState("PAUSED")}
                className={`py-1 text-[10px] font-medium rounded transition-colors ${
                  agentState === "PAUSED"
                    ? "bg-amber-600 text-white font-semibold"
                    : "bg-[#191d28] text-neutral-400 hover:text-white"
                }`}
              >
                Pausa
              </button>
              <button
                type="button"
                onClick={() => handleSetAgentState("MAINTENANCE")}
                className={`py-1 text-[10px] font-medium rounded transition-colors ${
                  agentState === "MAINTENANCE"
                    ? "bg-orange-600 text-white font-semibold"
                    : "bg-[#191d28] text-neutral-400 hover:text-white"
                }`}
              >
                Mant.
              </button>
            </div>
          </div>

          {/* KILL SWITCH BUTTON */}
          <button
            type="button"
            onClick={() => setKillSwitchModalOpen(true)}
            className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-md bg-red-950/40 hover:bg-red-900/60 text-red-400 border border-red-800/60 text-xs font-semibold tracking-wide transition-colors"
          >
            <Power className="w-3.5 h-3.5" />
            <span>Kill Switch</span>
          </button>
        </div>
      </aside>

      {/* ─── MAIN CONTENT AREA ─── */}
      <main className="flex-1 flex flex-col overflow-hidden bg-[#090a0f]">
        {/* Top Header */}
        <header className="h-16 px-8 border-b border-[#191c24] flex items-center justify-between shrink-0 bg-[#0c0e14]">
          <div className="flex items-center gap-4">
            <h1 className="text-sm font-semibold text-white uppercase tracking-wider">
              {activeTab === "overview" && "Panel Operacional"}
              {activeTab === "runs" && "Control de Ejecuciones & Aprobación Humana"}
              {activeTab === "conversations" && "Auditoría de Conversaciones en Sitio Web"}
              {activeTab === "knowledge" && "Base de Conocimiento Estructurada"}
              {activeTab === "rules" && "Reglas de Negocio Estructuradas"}
              {activeTab === "tools" && "Matriz de Capacidades y Autorización"}
              {activeTab === "workflows" && "Motor de Automatización y Flujos"}
              {activeTab === "integrations" && "Canales Conectados & Credenciales"}
              {activeTab === "billing" && "Gestión de Facturación y Prueba Gratuita"}
              {activeTab === "onboarding" && "Setup Guiado de 7 Pasos"}
            </h1>
            <div className="flex items-center gap-2 text-xs font-mono text-neutral-400">
              <span className="w-1.5 h-1.5 rounded-full bg-[#00F279]" />
              <span>Producción DEV (8001)</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={async () => {
                setRefreshing(true);
                await fetchOverview();
                setRefreshing(false);
                showToast("Datos actualizados desde el servidor", "info");
              }}
              className="p-2 rounded-md text-neutral-400 hover:text-white hover:bg-[#181c26] transition-colors"
              title="Actualizar datos"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin text-[#00F279]" : ""}`} />
            </button>

            <button
              type="button"
              onClick={copyScriptSnippet}
              className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-[#181c26] hover:bg-[#202533] text-neutral-200 border border-[#2b3142] text-xs font-medium transition-colors"
            >
              {copiedSnippet ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copiedSnippet ? "Copiado" : "Instalar en Web"}</span>
            </button>
          </div>
        </header>

        {/* Tab Body */}
        <div className="flex-1 overflow-y-auto p-8">
          {/* ═══════════════════════════════════════════════════════════════════
              TAB 1: OVERVIEW
              ═══════════════════════════════════════════════════════════════════ */}
          {activeTab === "overview" && (
            <div className="space-y-6 max-w-6xl mx-auto">
              {/* Free Trial Operational Banner */}
              {overview?.billing?.trial_active && (
                <div className="p-4 rounded-lg bg-[#0e1726] border border-blue-900/60 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-md bg-blue-900/40 text-blue-400">
                      <CreditCard className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-white uppercase tracking-wider">
                        Prueba 7 días gratis activa — {overview.billing.days_remaining} días restantes
                      </div>
                      <div className="text-xs text-neutral-400">
                        Próxima fecha de facturación: {overview.billing.next_billing_date} ({overview.billing.price_cop}). Cancela cuando quieras en 1 clic.
                      </div>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => setActiveTab("billing")}
                    className="px-3 py-1.5 rounded-md bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition-colors"
                  >
                    Detalles de prueba
                  </button>
                </div>
              )}

              {/* Real Metrics Grid */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-lg bg-[#11131a] border border-[#1d212c]">
                  <span className="text-xs text-neutral-400 font-medium block mb-1">Conversaciones Web</span>
                  <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-bold font-mono text-white">
                      {overview?.metrics?.total_conversations || 0}
                    </span>
                    <span className="text-xs text-emerald-400 font-mono">
                      +{overview?.metrics?.today_conversations || 0} hoy
                    </span>
                  </div>
                  <span className="text-[11px] text-neutral-500 mt-2 block">
                    Atendidas en tiempo real por el widget 2D
                  </span>
                </div>

                <div className="p-4 rounded-lg bg-[#11131a] border border-[#1d212c]">
                  <span className="text-xs text-neutral-400 font-medium block mb-1">Citas Confirmadas</span>
                  <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-bold font-mono text-white">
                      {overview?.metrics?.confirmed_appointments || 0}
                    </span>
                    <span className="text-xs text-neutral-500 font-mono">en Google Calendar</span>
                  </div>
                  <span className="text-[11px] text-neutral-500 mt-2 block">
                    Reservadas autónomamente sin error humano
                  </span>
                </div>

                <div className="p-4 rounded-lg bg-[#11131a] border border-[#1d212c]">
                  <span className="text-xs text-neutral-400 font-medium block mb-1">Aprobaciones HITL</span>
                  <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-bold font-mono text-white">
                      {overview?.metrics?.pending_approvals || 0}
                    </span>
                    <span className="text-xs text-amber-400 font-mono">pendientes</span>
                  </div>
                  <span className="text-[11px] text-neutral-500 mt-2 block">
                    Excepciones comerciales que esperan tu visto bueno
                  </span>
                </div>

                <div className="p-4 rounded-lg bg-[#11131a] border border-[#1d212c]">
                  <span className="text-xs text-neutral-400 font-medium block mb-1">Reglas & Flujos Activos</span>
                  <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-bold font-mono text-white">
                      {(overview?.metrics?.active_rules || 0) + (overview?.metrics?.active_workflows || 0)}
                    </span>
                    <span className="text-xs text-neutral-500 font-mono">en runtime</span>
                  </div>
                  <span className="text-[11px] text-neutral-500 mt-2 block">
                    Políticas deterministas aplicadas en cada turno
                  </span>
                </div>
              </div>

              {/* Web Installation Snippet Card */}
              <div className="p-5 rounded-lg bg-[#11131a] border border-[#1d212c]">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                      Instalación de Firby en tu Sitio Web
                    </h3>
                    <p className="text-xs text-neutral-400 mt-0.5">
                      Pega esta única línea de código antes de la etiqueta de cierre &lt;/body&gt; en tu sitio web.
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={copyScriptSnippet}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-[#1d212c] hover:bg-[#272c3b] text-neutral-200 text-xs font-medium transition-colors"
                  >
                    {copiedSnippet ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>Copiar Snippet</span>
                  </button>
                </div>
                <div className="p-3 rounded bg-[#090a0f] border border-[#191c24] font-mono text-xs text-[#00F279] overflow-x-auto">
                  <code>&lt;script src="https://firbyai.com/firby.js" data-agent="clinica-de-las-americas" async&gt;&lt;/script&gt;</code>
                </div>
              </div>

              {/* Natural Language Teaching Section */}
              <div className="p-5 rounded-lg bg-[#11131a] border border-[#1d212c]">
                <div className="mb-3">
                  <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                    Enseñar a Firby en Lenguaje Natural
                  </h3>
                  <p className="text-xs text-neutral-400 mt-0.5">
                    Escribe una instrucción comercial como le hablarías a un recepcionista. Firby la convertirá en conocimiento estructurado y regla de negocio en caliente.
                  </p>
                </div>
                <form onSubmit={handleTeachAgent} className="flex gap-2">
                  <input
                    type="text"
                    value={teachInstruction}
                    onChange={(e) => setTeachInstruction(e.target.value)}
                    placeholder="Ej: El horario de atención los sábados es hasta las 2:00 PM sin excepción."
                    className="flex-1 px-3 py-2 rounded bg-[#090a0f] border border-[#202533] text-xs text-white placeholder-neutral-500 focus:outline-none focus:border-[#00F279]"
                  />
                  <button
                    type="submit"
                    disabled={isTeaching || !teachInstruction.trim()}
                    className="px-4 py-2 rounded bg-[#00F279] hover:bg-[#00d66a] disabled:opacity-50 text-black text-xs font-bold transition-colors shrink-0"
                  >
                    {isTeaching ? "Procesando..." : "Enseñar a Firby"}
                  </button>
                </form>
              </div>

              {/* Recent Activity Audit Table */}
              <div className="p-5 rounded-lg bg-[#11131a] border border-[#1d212c]">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                    Registro de Actividad Operacional
                  </h3>
                  <span className="text-[11px] font-mono text-neutral-400">Auditoría Inmutable</span>
                </div>
                <div className="divide-y divide-[#191c24]">
                  {overview?.recent_activity && overview.recent_activity.length > 0 ? (
                    overview.recent_activity.map((item, idx) => (
                      <div key={idx} className="py-2.5 flex items-center justify-between text-xs">
                        <div className="flex items-center gap-3">
                          <span className="w-1.5 h-1.5 rounded-full bg-[#00F279]" />
                          <span className="font-mono text-neutral-200">{item.action}</span>
                          <span className="text-neutral-500 font-mono">por {item.actor}</span>
                        </div>
                        <span className="text-neutral-500 font-mono text-[11px]">{item.timestamp}</span>
                      </div>
                    ))
                  ) : (
                    <div className="py-4 text-center text-xs text-neutral-500">
                      No hay eventos registrados recientemente en este entorno.
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* ═══════════════════════════════════════════════════════════════════
              TAB 2: RUNS & APPROVALS (HITL)
              ═══════════════════════════════════════════════════════════════════ */}
          {activeTab === "runs" && (
            <div className="space-y-6 max-w-6xl mx-auto">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                    Turnos de Ejecución del Agente
                  </h2>
                  <p className="text-xs text-neutral-400">
                    Inspección paso a paso de ejecuciones activas, herramientas utilizadas y aprobaciones humanas pendientes.
                  </p>
                </div>
                <div className="flex gap-1.5">
                  {["all", "running", "waiting_approval", "completed", "cancelled"].map((f) => (
                    <button
                      key={f}
                      onClick={() => setRunsFilter(f)}
                      className={`px-2.5 py-1 text-xs rounded uppercase font-mono font-medium transition-colors ${
                        runsFilter === f
                          ? "bg-[#1f2433] text-white border border-[#2f374e]"
                          : "text-neutral-400 hover:text-white"
                      }`}
                    >
                      {f === "all" ? "Todos" : f}
                    </button>
                  ))}
                </div>
              </div>

              <div className="border border-[#1d212c] rounded-lg overflow-hidden bg-[#11131a]">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#0e1017] border-b border-[#1d212c] text-neutral-400 font-mono">
                    <tr>
                      <th className="py-3 px-4">Run ID</th>
                      <th className="py-3 px-4">Canal</th>
                      <th className="py-3 px-4">Usuario</th>
                      <th className="py-3 px-4">Estado</th>
                      <th className="py-3 px-4">Pasos</th>
                      <th className="py-3 px-4 text-right">Acciones</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#181b24]">
                    {runs
                      .filter((r) => runsFilter === "all" || r.state.toLowerCase() === runsFilter.toLowerCase())
                      .map((run) => (
                        <tr key={run.run_id} className="hover:bg-[#161922] transition-colors">
                          <td className="py-3 px-4 font-mono text-neutral-300">{run.run_id}</td>
                          <td className="py-3 px-4 text-neutral-400">{run.channel || "web"}</td>
                          <td className="py-3 px-4 font-mono text-neutral-400">{run.user_id}</td>
                          <td className="py-3 px-4">
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                                run.state === "RUNNING"
                                  ? "bg-blue-950 text-blue-400 border border-blue-900"
                                  : run.state === "WAITING_APPROVAL"
                                  ? "bg-amber-950 text-amber-400 border border-amber-800"
                                  : run.state === "COMPLETED"
                                  ? "bg-emerald-950 text-emerald-400 border border-emerald-900"
                                  : "bg-neutral-900 text-neutral-400 border border-neutral-800"
                              }`}
                            >
                              {run.state}
                            </span>
                          </td>
                          <td className="py-3 px-4 font-mono text-neutral-400">
                            {run.step_count || 1}/{run.max_steps || 6}
                          </td>
                          <td className="py-3 px-4 text-right space-x-2">
                            {run.state === "WAITING_APPROVAL" && (
                              <>
                                <button
                                  type="button"
                                  onClick={() => handleApproveRun(run.run_id)}
                                  className="px-2.5 py-1 rounded bg-emerald-700 hover:bg-emerald-600 text-white text-[11px] font-semibold transition-colors"
                                >
                                  Aprobar
                                </button>
                                <button
                                  type="button"
                                  onClick={() => handleDenyRun(run.run_id)}
                                  className="px-2.5 py-1 rounded bg-red-800 hover:bg-red-700 text-white text-[11px] font-semibold transition-colors"
                                >
                                  Rechazar
                                </button>
                              </>
                            )}
                            {run.state === "RUNNING" && (
                              <button
                                type="button"
                                onClick={() => handleCancelRun(run.run_id)}
                                className="px-2.5 py-1 rounded bg-neutral-800 hover:bg-neutral-700 text-neutral-300 text-[11px] transition-colors"
                              >
                                Cancelar
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    {runs.length === 0 && (
                      <tr>
                        <td colSpan={6} className="py-8 text-center text-neutral-500 font-mono text-xs">
                          No hay turnos activos registrados en este momento.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ═══════════════════════════════════════════════════════════════════
              TAB 3: CONVERSATIONS & OPERATIONAL EVENTS
              ═══════════════════════════════════════════════════════════════════ */}
          {activeTab === "conversations" && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto h-[calc(100vh-140px)]">
              {/* Left Column: Chat List */}
              <div className="border border-[#1d212c] rounded-lg bg-[#11131a] flex flex-col overflow-hidden">
                <div className="p-3 border-b border-[#1d212c] bg-[#0e1017]">
                  <span className="text-xs font-bold text-white uppercase tracking-wider">
                    Conversaciones Recientes
                  </span>
                </div>
                <div className="flex-1 overflow-y-auto divide-y divide-[#181b24]">
                  {conversations.map((c) => (
                    <button
                      key={c.chat_id}
                      type="button"
                      onClick={() => setSelectedChat(c)}
                      className={`w-full text-left p-3 hover:bg-[#161922] transition-colors ${
                        selectedChat?.chat_id === c.chat_id ? "bg-[#181c26]" : ""
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-semibold text-neutral-200">
                          {c.user_name || "Visitante Web"}
                        </span>
                        <span className="text-[10px] font-mono text-neutral-500">{c.updated_at}</span>
                      </div>
                      <p className="text-xs text-neutral-400 truncate">{c.last_message}</p>
                    </button>
                  ))}
                  {conversations.length === 0 && (
                    <div className="p-6 text-center text-xs text-neutral-500 font-mono">
                      No hay conversaciones registradas aún.
                    </div>
                  )}
                </div>
              </div>

              {/* Right Column: Chat Detail & Operational Timeline */}
              <div className="md:col-span-2 border border-[#1d212c] rounded-lg bg-[#11131a] flex flex-col overflow-hidden">
                {selectedChat ? (
                  <>
                    <div className="p-3.5 border-b border-[#1d212c] bg-[#0e1017] flex items-center justify-between">
                      <div>
                        <span className="text-xs font-bold text-white block">
                          {selectedChat.user_name || "Visitante Web"}
                        </span>
                        <span className="text-[10px] font-mono text-neutral-500">ID: {selectedChat.chat_id}</span>
                      </div>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-900">
                        Atención Web 2D
                      </span>
                    </div>

                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                      {chatDetail?.messages?.map((msg: any, i: number) => (
                        <div
                          key={i}
                          className={`flex flex-col ${msg.role === "user" ? "items-start" : "items-end"}`}
                        >
                          <div
                            className={`max-w-[80%] rounded-lg p-3 text-xs leading-relaxed ${
                              msg.role === "user"
                                ? "bg-[#1a1e2a] text-neutral-200 border border-[#252a3b]"
                                : "bg-[#0f2419] text-emerald-200 border border-emerald-900/60"
                            }`}
                          >
                            <span className="text-[10px] font-mono text-neutral-400 block mb-1">
                              {msg.role === "user" ? "Visitante" : "Firby Operador"} · {msg.timestamp}
                            </span>
                            <div>{msg.content}</div>
                          </div>

                          {/* Operational Events attached to turn */}
                          {msg.operational_events && msg.operational_events.length > 0 && (
                            <div className="mt-1 space-y-0.5 max-w-[80%]">
                              {msg.operational_events.map((ev: any, j: number) => (
                                <div
                                  key={j}
                                  className="text-[10px] font-mono text-neutral-400 flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#131620]"
                                >
                                  <Check className="w-2.5 h-2.5 text-[#00F279]" />
                                  <span>{ev.action}</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </>
                ) : (
                  <div className="flex-1 flex items-center justify-center text-xs text-neutral-500 font-mono">
                    Selecciona una conversación para auditar sus eventos en tiempo real.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ═══════════════════════════════════════════════════════════════════
              TAB 4: STRUCTURED KNOWLEDGE
              ═══════════════════════════════════════════════════════════════════ */}
          {activeTab === "knowledge" && (
            <div className="space-y-6 max-w-6xl mx-auto">
              {/* Add knowledge form */}
              <div className="p-5 rounded-lg bg-[#11131a] border border-[#1d212c]">
                <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-3">
                  Agregar Documento de Conocimiento Estructurado
                </h3>
                <form onSubmit={handleAddKnowledge} className="space-y-3">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <input
                      type="text"
                      value={newTitle}
                      onChange={(e) => setNewTitle(e.target.value)}
                      placeholder="Título del documento (ej: Política de Devoluciones)"
                      className="md:col-span-2 px-3 py-2 rounded bg-[#090a0f] border border-[#202533] text-xs text-white placeholder-neutral-500 focus:outline-none focus:border-[#00F279]"
                    />
                    <select
                      value={newCategory}
                      onChange={(e) => setNewCategory(e.target.value)}
                      className="px-3 py-2 rounded bg-[#090a0f] border border-[#202533] text-xs text-white focus:outline-none focus:border-[#00F279]"
                    >
                      <option value="business">General Negocio</option>
                      <option value="hours">Horarios y Atención</option>
                      <option value="pricing">Tarifas y Precios</option>
                      <option value="policies">Políticas Oficiales</option>
                      <option value="services">Servicios y Oferta</option>
                    </select>
                  </div>
                  <textarea
                    rows={3}
                    value={newContent}
                    onChange={(e) => setNewContent(e.target.value)}
                    placeholder="Contenido exacto del conocimiento corporativo..."
                    className="w-full px-3 py-2 rounded bg-[#090a0f] border border-[#202533] text-xs text-white placeholder-neutral-500 focus:outline-none focus:border-[#00F279]"
                  />
                  <div className="flex justify-end">
                    <button
                      type="submit"
                      disabled={!newTitle.trim() || !newContent.trim()}
                      className="px-4 py-2 rounded bg-[#00F279] hover:bg-[#00d66a] disabled:opacity-50 text-black text-xs font-bold transition-colors"
                    >
                      Guardar Documento
                    </button>
                  </div>
                </form>
              </div>

              {/* Knowledge items list */}
              <div className="border border-[#1d212c] rounded-lg overflow-hidden bg-[#11131a]">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#0e1017] border-b border-[#1d212c] text-neutral-400 font-mono">
                    <tr>
                      <th className="py-3 px-4">Título</th>
                      <th className="py-3 px-4">Categoría</th>
                      <th className="py-3 px-4">Versión</th>
                      <th className="py-3 px-4">Contenido</th>
                      <th className="py-3 px-4 text-right">Estado</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#181b24]">
                    {knowledgeList.map((k) => (
                      <tr key={k.doc_id} className="hover:bg-[#161922] transition-colors">
                        <td className="py-3 px-4 font-semibold text-neutral-200">{k.title}</td>
                        <td className="py-3 px-4">
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-neutral-800 text-neutral-300">
                            {k.category}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-mono text-neutral-400">v{k.version || 1}</td>
                        <td className="py-3 px-4 text-neutral-400 max-w-md truncate">{k.content}</td>
                        <td className="py-3 px-4 text-right">
                          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-900/60">
                            Activo
                          </span>
                        </td>
                      </tr>
                    ))}
                    {knowledgeList.length === 0 && (
                      <tr>
                        <td colSpan={5} className="py-8 text-center text-neutral-500 font-mono text-xs">
                          No hay documentos de conocimiento cargados aún.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ═══════════════════════════════════════════════════════════════════
              TAB 5: STRUCTURED RULES
              ═══════════════════════════════════════════════════════════════════ */}
          {activeTab === "rules" && (
            <div className="space-y-6 max-w-6xl mx-auto">
              {/* Add rule form */}
              <div className="p-5 rounded-lg bg-[#11131a] border border-[#1d212c]">
                <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-3">
                  Crear Regla de Negocio Estructurada
                </h3>
                <form onSubmit={handleCreateRule} className="space-y-3">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <input
                      type="text"
                      value={newCondition}
                      onChange={(e) => setNewCondition(e.target.value)}
                      placeholder="Condición / Trigger (Ej: Si piden descuento mayor al 15%)"
                      className="px-3 py-2 rounded bg-[#090a0f] border border-[#202533] text-xs text-white placeholder-neutral-500 focus:outline-none focus:border-[#00F279]"
                    />
                    <input
                      type="text"
                      value={newDirective}
                      onChange={(e) => setNewDirective(e.target.value)}
                      placeholder="Directiva / Acción (Ej: Solicitar aprobación humana en Telegram/WhatsApp)"
                      className="px-3 py-2 rounded bg-[#090a0f] border border-[#202533] text-xs text-white placeholder-neutral-500 focus:outline-none focus:border-[#00F279]"
                    />
                  </div>
                  <div className="flex justify-end">
                    <button
                      type="submit"
                      disabled={!newCondition.trim() || !newDirective.trim()}
                      className="px-4 py-2 rounded bg-[#00F279] hover:bg-[#00d66a] disabled:opacity-50 text-black text-xs font-bold transition-colors"
                    >
                      Crear Regla
                    </button>
                  </div>
                </form>
              </div>

              {/* Rules list */}
              <div className="border border-[#1d212c] rounded-lg overflow-hidden bg-[#11131a]">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#0e1017] border-b border-[#1d212c] text-neutral-400 font-mono">
                    <tr>
                      <th className="py-3 px-4">Condición</th>
                      <th className="py-3 px-4">Directiva Operacional</th>
                      <th className="py-3 px-4">Categoría</th>
                      <th className="py-3 px-4 text-right">Interruptor</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#181b24]">
                    {rules.map((r) => (
                      <tr key={r.id || r.rule_id} className="hover:bg-[#161922] transition-colors">
                        <td className="py-3 px-4 font-mono text-neutral-200">{r.trigger_condition}</td>
                        <td className="py-3 px-4 text-neutral-300">{r.directive}</td>
                        <td className="py-3 px-4">
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-neutral-800 text-neutral-400">
                            {r.category || "policy"}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right">
                          <button
                            type="button"
                            onClick={() => handleToggleRule(r.id || r.rule_id, r.is_active)}
                            className={`px-3 py-1 rounded text-xs font-mono font-semibold transition-colors ${
                              r.is_active
                                ? "bg-emerald-950 text-emerald-400 border border-emerald-800 hover:bg-emerald-900"
                                : "bg-neutral-900 text-neutral-500 border border-neutral-800 hover:text-neutral-300"
                            }`}
                          >
                            {r.is_active ? "Activa" : "Inactiva"}
                          </button>
                        </td>
                      </tr>
                    ))}
                    {rules.length === 0 && (
                      <tr>
                        <td colSpan={4} className="py-8 text-center text-neutral-500 font-mono text-xs">
                          No hay reglas registradas aún.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ═══════════════════════════════════════════════════════════════════
              TAB 6: CAPABILITY MATRIX & TOOLS
              ═══════════════════════════════════════════════════════════════════ */}
          {activeTab === "tools" && (
            <div className="space-y-6 max-w-6xl mx-auto">
              <div>
                <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                  Matriz de Herramientas y Capacidades
                </h2>
                <p className="text-xs text-neutral-400">
                  Controla de forma granular qué acciones puede ejecutar Firby y cuáles requieren visto bueno humano.
                </p>
              </div>

              <div className="border border-[#1d212c] rounded-lg overflow-hidden bg-[#11131a]">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#0e1017] border-b border-[#1d212c] text-neutral-400 font-mono">
                    <tr>
                      <th className="py-3 px-4">Capacidad</th>
                      <th className="py-3 px-4">Nivel de Permiso</th>
                      <th className="py-3 px-4">Habilitada</th>
                      <th className="py-3 px-4 text-right">Supervisión Humana (HITL)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#181b24]">
                    {tools.map((t) => (
                      <tr key={t.id} className="hover:bg-[#161922] transition-colors">
                        <td className="py-3 px-4 font-mono text-neutral-200">
                          {t.id}
                          {t.reason && (
                            <span className="block text-[10px] text-neutral-500 font-sans">{t.reason}</span>
                          )}
                        </td>
                        <td className="py-3 px-4 font-mono text-neutral-400 uppercase">{t.permission_level || "read"}</td>
                        <td className="py-3 px-4">
                          <button
                            type="button"
                            onClick={() => handleToggleTool(t.id, t.is_active, t.requires_hitl)}
                            className={`px-3 py-1 rounded text-xs font-mono font-semibold transition-colors ${
                              t.is_active
                                ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                                : "bg-neutral-900 text-neutral-500 border border-neutral-800"
                            }`}
                          >
                            {t.is_active ? "Habilitada" : "Deshabilitada"}
                          </button>
                        </td>
                        <td className="py-3 px-4 text-right">
                          <button
                            type="button"
                            onClick={() => handleToggleToolHitl(t.id, t.is_active, t.requires_hitl)}
                            className={`px-3 py-1 rounded text-xs font-mono font-semibold transition-colors ${
                              t.requires_hitl
                                ? "bg-amber-950 text-amber-400 border border-amber-800"
                                : "bg-neutral-900 text-neutral-500 border border-neutral-800"
                            }`}
                          >
                            {t.requires_hitl ? "Exige Aprobación" : "Autónoma"}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ═══════════════════════════════════════════════════════════════════
              TAB 7: WORKFLOWS (EL N8N DE FIRBY) & DRY-RUN SIMULATOR
              ═══════════════════════════════════════════════════════════════════ */}
          {activeTab === "workflows" && (
            <div className="space-y-6 max-w-6xl mx-auto">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                    Motor de Flujos Deterministas ("El n8n de Firby")
                  </h2>
                  <p className="text-xs text-neutral-400">
                    Diseño y simulación paso a paso de flujos con nodos de Disparo, Condición, Acción y Aprobación.
                  </p>
                </div>
              </div>

              {/* Workflow Selector */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                {workflows.map((wf) => (
                  <button
                    key={wf.id || wf.workflow_id}
                    type="button"
                    onClick={() => {
                      setSelectedWorkflow(wf);
                      setDryRunResult(null);
                    }}
                    className={`p-3 rounded-lg border text-left transition-colors ${
                      (selectedWorkflow?.id || selectedWorkflow?.workflow_id) === (wf.id || wf.workflow_id)
                        ? "bg-[#181c26] border-[#00F279] text-white"
                        : "bg-[#11131a] border-[#1d212c] text-neutral-300 hover:border-neutral-600"
                    }`}
                  >
                    <div className="text-xs font-bold truncate">{wf.name}</div>
                    <div className="text-[11px] text-neutral-400 line-clamp-2 mt-1">{wf.description}</div>
                    <div className="mt-2 flex items-center justify-between text-[10px] font-mono text-neutral-500">
                      <span>v{wf.version || 1}</span>
                      <span className="uppercase text-[#00F279]">{wf.status}</span>
                    </div>
                  </button>
                ))}
              </div>

              {/* Flow Graph & Dry Run Simulator Side-by-Side */}
              {selectedWorkflow && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Left: Nodes Breakdown */}
                  <div className="p-5 rounded-lg bg-[#11131a] border border-[#1d212c] space-y-4">
                    <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                      Grafo del Flujo: {selectedWorkflow.name}
                    </h3>
                    <div className="space-y-2">
                      {selectedWorkflow.definition?.nodes &&
                        Object.values(selectedWorkflow.definition.nodes).map((node: any, idx: number) => (
                          <div
                            key={node.id}
                            className="p-3 rounded bg-[#0e1017] border border-[#1d212c] flex items-center justify-between"
                          >
                            <div className="flex items-center gap-2.5">
                              <span className="text-[10px] font-mono text-neutral-500">{idx + 1}.</span>
                              <div>
                                <span className="text-xs font-semibold text-neutral-200 block">
                                  {node.name || node.id}
                                </span>
                                <span className="text-[10px] font-mono text-neutral-400 uppercase">
                                  {node.type} {node.sub_type && `(${node.sub_type})`}
                                </span>
                              </div>
                            </div>
                            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-neutral-800 text-neutral-300">
                              {node.next_node_id ? `-> ${node.next_node_id}` : "Fin"}
                            </span>
                          </div>
                        ))}
                    </div>
                  </div>

                  {/* Right: Dry Run Simulator */}
                  <div className="p-5 rounded-lg bg-[#11131a] border border-[#1d212c] space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                        Simulador Dry-Run (Sandbox Seguro)
                      </h3>
                      <button
                        type="button"
                        onClick={handleRunSimulator}
                        disabled={isDryRunning}
                        className="px-3 py-1 rounded bg-[#00F279] hover:bg-[#00d66a] disabled:opacity-50 text-black text-xs font-bold transition-colors"
                      >
                        {isDryRunning ? "Simulando..." : "Ejecutar Dry-Run"}
                      </button>
                    </div>

                    <div>
                      <span className="text-[11px] text-neutral-400 font-mono block mb-1">
                        Payload de Prueba (JSON):
                      </span>
                      <textarea
                        rows={4}
                        value={dryRunPayload}
                        onChange={(e) => setDryRunPayload(e.target.value)}
                        className="w-full p-2.5 rounded bg-[#090a0f] border border-[#202533] font-mono text-xs text-[#00F279] focus:outline-none"
                      />
                    </div>

                    {/* Simulator Trace Output */}
                    {dryRunResult && (
                      <div className="space-y-2 border-t border-[#1d212c] pt-3">
                        <div className="flex items-center justify-between text-xs font-mono">
                          <span className="text-neutral-300 font-semibold">Traza de Ejecución:</span>
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              dryRunResult.status === "COMPLETED"
                                ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                                : "bg-red-950 text-red-400 border border-red-800"
                            }`}
                          >
                            {dryRunResult.status} ({dryRunResult.total_steps || 0} pasos)
                          </span>
                        </div>
                        <div className="space-y-1.5 max-h-56 overflow-y-auto">
                          {dryRunResult.steps?.map((st: any) => (
                            <div
                              key={st.step}
                              className="p-2 rounded bg-[#090a0f] border border-[#191c24] text-[11px] font-mono"
                            >
                              <div className="flex items-center justify-between text-neutral-400">
                                <span>
                                  Paso {st.step}: {st.node_name}
                                </span>
                                <span className="text-[#00F279]">{st.action}</span>
                              </div>
                              {st.condition_evaluation && (
                                <div className="text-[10px] text-amber-400 mt-0.5">
                                  Evaluación: {st.condition_evaluation.variable} {st.condition_evaluation.operator}{" "}
                                  {st.condition_evaluation.target} =&gt;{" "}
                                  {st.condition_evaluation.result ? "VERDADERO" : "FALSO"}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ═══════════════════════════════════════════════════════════════════
              TAB 8: INTEGRATIONS & CHANNELS
              ═══════════════════════════════════════════════════════════════════ */}
          {activeTab === "integrations" && (
            <div className="space-y-6 max-w-6xl mx-auto">
              <div>
                <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                  Canales & Integraciones Conectadas
                </h2>
                <p className="text-xs text-neutral-400">
                  Las credenciales se encriptan y procesan 100% en backend; ningún token se expone al cliente.
                </p>
              </div>

              {/* Integrations Status Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {integrations.map((it) => (
                  <div key={it.id} className="p-4 rounded-lg bg-[#11131a] border border-[#1d212c] space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-white uppercase tracking-wider">{it.name}</span>
                      <span
                        className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold uppercase ${
                          it.connected || it.status === "CONNECTED"
                            ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                            : "bg-neutral-900 text-neutral-500 border border-neutral-800"
                        }`}
                      >
                        {it.connected || it.status === "CONNECTED" ? "Conectado" : "No Conectado"}
                      </span>
                    </div>
                    <p className="text-xs text-neutral-400">
                      {it.id === "web_widget" && "Atención de visitantes en tiempo real en tu sitio web."}
                      {it.id === "meta_whatsapp" && "Línea ejecutiva continua privada exclusivamente para el dueño (+57 324 369 9856)."}
                      {it.id === "google_calendar" && "Lectura y bloqueo de disponibilidad en tu calendario oficial."}
                      {it.id === "crm_webhooks" && "Disparo de eventos con firma criptográfica HMAC SHA-256."}
                    </p>
                  </div>
                ))}
              </div>

              {/* Meta WhatsApp Setup Card */}
              <div className="p-5 rounded-lg bg-[#11131a] border border-[#1d212c] space-y-3">
                <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                  Configurar Meta WhatsApp Business Cloud API (Línea Privada Dueño)
                </h3>
                <form onSubmit={handleSaveWhatsApp} className="space-y-3">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <input
                      type="text"
                      value={waPhoneNumberId}
                      onChange={(e) => setWaPhoneNumberId(e.target.value)}
                      placeholder="Phone Number ID de Meta (Ej: 10023456789)"
                      className="px-3 py-2 rounded bg-[#090a0f] border border-[#202533] text-xs text-white placeholder-neutral-500 focus:outline-none"
                    />
                    <input
                      type="text"
                      value={waBusinessAccountId}
                      onChange={(e) => setWaBusinessAccountId(e.target.value)}
                      placeholder="WhatsApp Business Account ID (WABA)"
                      className="px-3 py-2 rounded bg-[#090a0f] border border-[#202533] text-xs text-white placeholder-neutral-500 focus:outline-none"
                    />
                  </div>
                  <input
                    type="password"
                    value={waAccessToken}
                    onChange={(e) => setWaAccessToken(e.target.value)}
                    placeholder="System User Permanent Access Token (EAAX...)"
                    className="w-full px-3 py-2 rounded bg-[#090a0f] border border-[#202533] text-xs text-white placeholder-neutral-500 focus:outline-none"
                  />
                  <div className="flex justify-end">
                    <button
                      type="submit"
                      className="px-4 py-2 rounded bg-[#00F279] hover:bg-[#00d66a] text-black text-xs font-bold transition-colors"
                    >
                      Guardar Credenciales Seguras
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {/* ═══════════════════════════════════════════════════════════════════
              TAB 9: BILLING & FREE TRIAL (1-CLICK CANCEL)
              ═══════════════════════════════════════════════════════════════════ */}
          {activeTab === "billing" && (
            <div className="space-y-6 max-w-4xl mx-auto">
              <div className="p-6 rounded-lg bg-[#11131a] border border-[#1d212c] space-y-4">
                <div className="flex items-center justify-between border-b border-[#1d212c] pb-4">
                  <div>
                    <h2 className="text-base font-bold text-white">
                      {overview?.billing?.plan_name || "Plan Pro"}
                    </h2>
                    <span className="text-xs text-neutral-400">
                      {overview?.billing?.price_cop || "$490.000 COP / mes"}
                    </span>
                  </div>
                  <span
                    className={`px-3 py-1 rounded text-xs font-mono font-bold uppercase ${
                      overview?.billing?.trial_status === "CANCELLED"
                        ? "bg-red-950 text-red-400 border border-red-800"
                        : "bg-emerald-950 text-emerald-400 border border-emerald-800"
                    }`}
                  >
                    {overview?.billing?.trial_status === "CANCELLED"
                      ? "Cancelada"
                      : `Prueba Activa (${overview?.billing?.days_remaining || 7} días restantes)`}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono text-neutral-300">
                  <div>
                    <span className="text-neutral-500 block mb-1">Próxima Facturación:</span>
                    <span>{overview?.billing?.next_billing_date || "En 7 días"}</span>
                  </div>
                  <div>
                    <span className="text-neutral-500 block mb-1">Método de Verificación:</span>
                    <span>Tarjeta de seguridad (•••• 4242)</span>
                  </div>
                </div>

                <div className="p-4 rounded bg-[#090a0f] border border-[#1d212c] text-xs text-neutral-400 space-y-2">
                  <div className="font-semibold text-white">Política de Cancelación Firby:</div>
                  <p>{overview?.billing?.cancel_policy || "Cancela en 1 clic en cualquier momento sin penalidad ni cargos pendientes."}</p>
                </div>

                {overview?.billing?.can_cancel && (
                  <div className="pt-2 flex justify-end">
                    <button
                      type="button"
                      onClick={() => setCancelBillingModalOpen(true)}
                      className="px-4 py-2 rounded bg-red-950/60 hover:bg-red-900 text-red-300 border border-red-800/60 text-xs font-semibold transition-colors"
                    >
                      Cancelar Suscripción en 1 Clic
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ═══════════════════════════════════════════════════════════════════
              TAB 10: ONBOARDING (7 STEPS)
              ═══════════════════════════════════════════════════════════════════ */}
          {activeTab === "onboarding" && (
            <div className="space-y-6 max-w-4xl mx-auto">
              <div className="p-5 rounded-lg bg-[#11131a] border border-[#1d212c]">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                    Progreso de Configuración Inicial (7 Pasos)
                  </h2>
                  <span className="text-xs font-mono text-[#00F279] font-bold">
                    {onboarding?.progress_percentage || 0}% Completado
                  </span>
                </div>
                <div className="w-full h-2 rounded bg-[#090a0f] overflow-hidden">
                  <div
                    className="h-full bg-[#00F279] transition-all duration-500"
                    style={{ width: `${onboarding?.progress_percentage || 0}%` }}
                  />
                </div>
              </div>

              <div className="space-y-2">
                {onboarding?.steps?.map((step: any) => (
                  <div
                    key={step.id}
                    className="p-4 rounded-lg bg-[#11131a] border border-[#1d212c] flex items-center justify-between"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-6 h-6 rounded-full flex items-center justify-center font-mono text-xs font-bold ${
                          step.done || step.completed
                            ? "bg-[#00F279] text-black"
                            : "bg-neutral-800 text-neutral-400"
                        }`}
                      >
                        {step.done || step.completed ? <Check className="w-3.5 h-3.5" /> : step.id}
                      </div>
                      <span
                        className={`text-xs font-semibold ${
                          step.done || step.completed ? "text-neutral-200" : "text-neutral-400"
                        }`}
                      >
                        {step.title}
                      </span>
                    </div>

                    {!(step.done || step.completed) && (
                      <button
                        type="button"
                        onClick={() => handleCompleteOnboardingStep(step.step_key || String(step.id))}
                        className="px-3 py-1 rounded bg-[#181c26] hover:bg-[#202533] text-white text-xs font-medium border border-[#2b3142] transition-colors"
                      >
                        Completar Paso
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>

      {/* ─── MODAL: EMERGENCY STOP KILL SWITCH ─── */}
      {killSwitchModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-[#12141c] border border-red-900 rounded-lg p-6 space-y-4 shadow-2xl">
            <div className="flex items-center gap-3 text-red-400">
              <AlertOctagon className="w-6 h-6" />
              <h3 className="text-sm font-bold uppercase tracking-wider">Confirmar Parada de Emergencia</h3>
            </div>
            <p className="text-xs text-neutral-300 leading-relaxed">
              Esta acción activará el <strong>Kill Switch</strong> de Firby:
            </p>
            <ul className="text-xs text-neutral-400 space-y-1 list-disc list-inside">
              <li>Pausará inmediatamente todas las respuestas del agente en tu sitio web.</li>
              <li>Abortará todos los turnos y herramientas en ejecución.</li>
              <li>Generará un registro de auditoría de seguridad inmutable.</li>
            </ul>
            <div className="flex justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setKillSwitchModalOpen(false)}
                className="px-4 py-2 rounded bg-neutral-800 hover:bg-neutral-700 text-neutral-300 text-xs font-medium transition-colors"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={handleEmergencyStop}
                className="px-4 py-2 rounded bg-red-600 hover:bg-red-500 text-white text-xs font-bold transition-colors"
              >
                Activar Kill Switch
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ─── MODAL: CANCEL BILLING ─── */}
      {cancelBillingModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-[#12141c] border border-[#262b3b] rounded-lg p-6 space-y-4 shadow-2xl">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Cancelar Suscripción en 1 Clic
            </h3>
            <p className="text-xs text-neutral-300 leading-relaxed">
              ¿Confirmas la cancelación de tu suscripción? Tu periodo de prueba finalizará y no se aplicará ningún cobro automático a tu tarjeta.
            </p>
            <div className="flex justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setCancelBillingModalOpen(false)}
                className="px-4 py-2 rounded bg-neutral-800 hover:bg-neutral-700 text-neutral-300 text-xs font-medium transition-colors"
              >
                Mantener Suscripción
              </button>
              <button
                type="button"
                onClick={handleCancelBilling}
                className="px-4 py-2 rounded bg-red-600 hover:bg-red-500 text-white text-xs font-bold transition-colors"
              >
                Confirmar Cancelación
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
