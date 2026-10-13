"use client";

import React, { useState, useMemo, useCallback } from "react";
import { AppShell } from "@/components/app-shell";
import {
  ChevronDown,
  ChevronLeft,
  Filter,
  MoreVertical,
  Home,
  Globe,
  GitBranch,
  RotateCcw,
  Plus,
  Search,
  Copy,
  PanelRightClose,
  CheckCircle2,
  Clock,
  X,
  Code,
  Check,
  Trash2,
  Pencil,
  Download,
  Pause,
  Play,
  Maximize2,
  Minimize2,
  ZoomIn,
  ZoomOut,
  Sparkles,
} from "lucide-react";
import {
  ReactFlow,
  Background,
  Handle,
  Position,
  BackgroundVariant,
  NodeProps,
  useReactFlow,
  ReactFlowProvider,
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  addEdge,
  OnConnect,
  NodeToolbar,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

// ── TIPOS DE DATOS ───────────────────────────────────────────────────────────
type TabKey = "flujos" | "credenciales" | "ejecuciones" | "variables" | "tablas";
type InteriorTabKey = "editor" | "ejecuciones" | "evaluaciones";

interface FlowItem {
  id: string;
  name: string;
  description: string;
  status: "Publicado" | "Borrador" | "Pausado";
  lastRun: string;
  createdBy: string;
  triggerType: string;
  tags: string[];
}

interface ExecutionItem {
  id: string;
  flowName: string;
  status: "Completado" | "Fallido" | "En ejecución";
  startTime: string;
  duration: string;
}

interface CredentialItem {
  id: string;
  name: string;
  service: string;
  scope: "Personal" | "Compartido";
  serviceType: "calendar" | "whatsapp" | "firby" | "webhook";
}

interface WorkflowNodeData extends Record<string, unknown> {
  label: string;
  subtitle?: string;
  nodeType: "trigger" | "transform" | "conditional" | "action" | "webhookPreview";
  integration?: "telegram" | "whatsapp" | "calendar" | "webhook" | "transform";
  iconColor?: string;
  statusBadge?: string;
  isExecuting?: boolean;
  isSuccess?: boolean;
}

type WorkflowNode = Node<WorkflowNodeData>;

// ── FLUJOS OFICIALES ─────────────────────────────────────────────────────────
const INITIAL_FLOWS: FlowItem[] = [
  {
    id: "wf-1",
    name: "Agendamiento Autónomo en Sitio Web",
    description: "Atención 24/7 en web y consulta Google Calendar",
    status: "Publicado",
    lastRun: "Hace 12 min",
    createdBy: "Santiago Rubio",
    triggerType: "Sitio Web 2D",
    tags: ["Producción", "Google Calendar"],
  },
  {
    id: "wf-2",
    name: "Alerta WhatsApp a Dueño por Excepciones",
    description: "Visto bueno exclusivo a +57 324 369 9856",
    status: "Publicado",
    lastRun: "Hace 45 min",
    createdBy: "Santiago Rubio",
    triggerType: "Webhook Comercial",
    tags: ["WhatsApp Privado"],
  },
  {
    id: "wf-3",
    name: "Captura y Calificación de Leads Nocturnos",
    description: "Filtro fuera de horario comercial con llamada matutina",
    status: "Publicado",
    lastRun: "Ayer 22:40",
    createdBy: "Santiago Rubio",
    triggerType: "Horario Nocturno",
    tags: ["Automatización"],
  },
];

const INITIAL_EXECUTIONS: ExecutionItem[] = [
  {
    id: "exec-101",
    flowName: "Agendamiento Autónomo en Sitio Web",
    status: "Completado",
    startTime: "Hace 12 min",
    duration: "142 ms",
  },
  {
    id: "exec-102",
    flowName: "Alerta WhatsApp a Dueño por Excepciones",
    status: "Completado",
    startTime: "Hace 45 min",
    duration: "88 ms",
  },
  {
    id: "exec-103",
    flowName: "Captura y Calificación de Leads Nocturnos",
    status: "Completado",
    startTime: "Ayer 22:40",
    duration: "210 ms",
  },
  {
    id: "exec-104",
    flowName: "Agendamiento Autónomo en Sitio Web",
    status: "Completado",
    startTime: "Ayer 19:15",
    duration: "134 ms",
  },
];

const INITIAL_CREDENTIALS: CredentialItem[] = [
  {
    id: "cred-1",
    name: "Google Calendar Principal",
    service: "OAuth2 · citas-principales@firbyai.com",
    scope: "Compartido",
    serviceType: "calendar",
  },
  {
    id: "cred-2",
    name: "Línea Ejecutiva WhatsApp",
    service: "WhatsApp Cloud API · +57 324 369 9856",
    scope: "Personal",
    serviceType: "whatsapp",
  },
  {
    id: "cred-3",
    name: "Firby LLM Core",
    service: "Modelo firby-v9.6-realtime · Conexión directa",
    scope: "Compartido",
    serviceType: "firby",
  },
  {
    id: "cred-4",
    name: "Webhook Widget 2D",
    service: "Disparador en vivo de sitio web",
    scope: "Compartido",
    serviceType: "webhook",
  },
];

// ── LOGOS REALES DE INTEGRACIONES (OFICIALES DE N8N) ────────────────────────
export function GoogleCalendarLogo({ className = "size-5" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 81 82"
      className={className}
      fillRule="evenodd"
      strokeLinecap="round"
      strokeLinejoin="round"
      xmlns="http://www.w3.org/2000/svg"
    >
      <g fillRule="nonzero" stroke="none">
        <path fill="#ffffff" d="M61.052 18.947H18.947v42.105h42.105z" />
        <path fill="#ea4335" d="M61.053 80 80 61.053H61.053z" />
        <path fill="#fbbc04" d="M80 18.947H61.053v42.105H80z" />
        <path fill="#34a853" d="M61.052 61.053H18.947V80h42.105z" />
        <path fill="#188038" d="M0 61.053v12.632A6.314 6.314 0 0 0 6.316 80h12.632V61.053z" />
        <path fill="#1967d2" d="M80 18.947V6.316A6.314 6.314 0 0 0 73.685 0H61.053v18.947z" />
        <path
          fill="#4285f4"
          d="M61.053 0H6.316A6.314 6.314 0 0 0 0 6.316v54.737h18.947V18.947h42.105V0zM27.584 51.611c-1.574-1.063-2.663-2.616-3.258-4.668l3.653-1.505q.498 1.894 1.737 2.937c1.239 1.043 1.821 1.037 2.989 1.037q1.792 0 3.079-1.089c1.287-1.089 1.29-1.653 1.29-2.774a3.44 3.44 0 0 0-1.358-2.811c-.905-.727-2.042-1.089-3.4-1.089h-2.111v-3.616H32.1q1.752 0 2.953-.947c1.201-.947 1.2-1.495 1.2-2.595q0-1.467-1.074-2.342c-1.074-.875-1.621-.879-2.721-.879q-1.61-.002-2.558.858c-.948.86-1.106 1.301-1.379 2.111l-3.616-1.505c.479-1.358 1.358-2.558 2.647-3.595s2.937-1.558 4.937-1.558q2.22-.002 3.989.858c1.769.86 2.105 1.368 2.774 2.379s1 2.153 1 3.416q0 1.932-.932 3.274c-.932 1.342-1.384 1.579-2.289 2.058v.216a6.95 6.95 0 0 1 2.937 2.289q1.146 1.538 1.147 3.684c.001 2.146-.363 2.711-1.089 3.832s-1.732 2.005-3.005 2.647c-1.279.642-2.716.968-4.311.968-1.847.005-3.553-.526-5.126-1.589zm22.437-18.126-4.01 2.9-2.005-3.042 7.195-5.189h2.758v24.479h-3.937V33.484z"
        />
      </g>
    </svg>
  );
}

export function WhatsAppLogo({ className = "size-5" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 48 48"
      className={className}
      fillRule="evenodd"
      clipRule="evenodd"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        fill="#ffffff"
        d="m4.868 43.303 2.694-9.835a18.94 18.94 0 0 1-2.535-9.489C5.032 13.514 13.548 5 24.014 5a18.87 18.87 0 0 1 13.43 5.566A18.87 18.87 0 0 1 43 23.994c-.004 10.465-8.522 18.98-18.986 18.98h-.008a19 19 0 0 1-9.073-2.311z"
      />
      <path
        fill="#cfd8dc"
        d="M24.014 5a18.87 18.87 0 0 1 13.43 5.566A18.87 18.87 0 0 1 43 23.994c-.004 10.465-8.522 18.98-18.986 18.98h-.008a19 19 0 0 1-9.073-2.311l-10.065 2.64 2.694-9.835a18.94 18.94 0 0 1-2.535-9.489C5.032 13.514 13.548 5 24.014 5m0-1C12.998 4 4.032 12.962 4.027 23.979a20 20 0 0 0 2.461 9.622L3.903 43.04a.998.998 0 0 0 1.219 1.231l9.687-2.54a20 20 0 0 0 9.197 2.244c11.024 0 19.99-8.963 19.995-19.98A19.86 19.86 0 0 0 38.153 9.86 19.87 19.87 0 0 0 24.014 4"
      />
      <path
        fill="#25D366"
        d="M35.176 12.832a15.67 15.67 0 0 0-11.157-4.626c-8.704 0-15.783 7.076-15.787 15.774a15.74 15.74 0 0 0 2.413 8.396l.376.597-1.595 5.821 5.973-1.566.577.342a15.75 15.75 0 0 0 8.032 2.199h.006c8.698 0 15.777-7.077 15.78-15.776a15.68 15.68 0 0 0-4.618-11.161"
      />
      <path
        fill="#ffffff"
        d="M19.268 16.045c-.355-.79-.729-.806-1.068-.82-.277-.012-.593-.011-.909-.011s-.83.119-1.265.594-1.661 1.622-1.661 3.956 1.7 4.59 1.937 4.906 3.282 5.259 8.104 7.161c4.007 1.58 4.823 1.266 5.693 1.187s2.807-1.147 3.202-2.255.395-2.057.277-2.255c-.119-.198-.435-.316-.909-.554s-2.807-1.385-3.242-1.543-.751-.237-1.068.238c-.316.474-1.225 1.543-1.502 1.859s-.554.357-1.028.119-2.002-.738-3.815-2.354c-1.41-1.257-2.362-2.81-2.639-3.285-.277-.474-.03-.731.208-.968.213-.213.474-.554.712-.831.237-.277.316-.475.474-.791s.079-.594-.04-.831c-.117-.238-1.039-2.584-1.461-3.522"
      />
    </svg>
  );
}

export function TelegramLogo({ className = "size-5" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 66 66"
      className={className}
      fillRule="evenodd"
      strokeLinecap="round"
      strokeLinejoin="round"
      xmlns="http://www.w3.org/2000/svg"
    >
      <g fillRule="nonzero" stroke="none">
        <path
          fill="#37aee2"
          d="M0 32c0 17.673 14.327 32 32 32s32-14.327 32-32S49.673 0 32 0 0 14.327 0 32"
        />
        <path
          fill="#c8daea"
          d="m21.661 34.338 3.797 10.508s.475.983.983.983 8.068-7.864 8.068-7.864l8.407-16.237-21.119 9.898z"
        />
        <path
          fill="#a9c6d8"
          d="m26.695 37.034-.729 7.746s-.305 2.373 2.068 0l4.644-4.203"
        />
        <path
          fill="#ffffff"
          d="m21.73 34.712-7.809-2.545s-.932-.378-.633-1.237c.062-.177.186-.328.559-.588 1.731-1.206 32.028-12.096 32.028-12.096s.856-.288 1.361-.097c.231.088.378.187.503.548.045.132.071.411.068.689-.003.201-.027.386-.045.678-.184 2.978-5.706 25.198-5.706 25.198s-.33 1.3-1.514 1.345c-.432.016-.956-.071-1.582-.61-2.323-1.998-10.352-7.394-12.126-8.58a.34.34 0 0 1-.146-.239c-.025-.125.108-.28.108-.28s13.98-12.427 14.352-13.731c.029-.101-.079-.151-.226-.107-.929.342-17.025 10.506-18.801 11.629-.104.066-.395.023-.395.023"
        />
      </g>
    </svg>
  );
}

function ServiceLogo({ type }: { type: CredentialItem["serviceType"] }) {
  if (type === "calendar") {
    return (
      <div className="size-8 rounded-[8px] bg-white/[0.05] border border-white/[0.1] flex items-center justify-center shrink-0 p-1 shadow-xs">
        <GoogleCalendarLogo className="size-5 shrink-0" />
      </div>
    );
  }
  if (type === "whatsapp") {
    return (
      <div className="size-8 rounded-[8px] bg-[#25D366]/[0.08] border border-[#25D366]/25 flex items-center justify-center shrink-0 p-1 shadow-xs">
        <WhatsAppLogo className="size-5 shrink-0" />
      </div>
    );
  }
  if (type === "firby") {
    return (
      <div className="size-8 rounded-[8px] bg-purple-500/[0.08] border border-purple-500/20 flex items-center justify-center shrink-0 shadow-xs">
        <svg className="size-4 shrink-0" viewBox="0 0 24 24" fill="none">
          <polygon points="12,2 22,8.5 22,15.5 12,22 2,15.5 2,8.5" stroke="#a855f7" strokeWidth="2" />
          <circle cx="12" cy="12" r="2.5" fill="#b9fa01" />
        </svg>
      </div>
    );
  }
  return (
    <div className="size-8 rounded-[8px] bg-orange-500/[0.08] border border-orange-500/20 flex items-center justify-center shrink-0 shadow-xs">
      <svg className="size-4 shrink-0" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="9" stroke="#f97316" strokeWidth="2" />
        <path d="M12 3v18M3 12h18" stroke="#f97316" strokeWidth="1.5" />
      </svg>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECCIÓN 7 & 8: ANATOMÍA GENÉRICA DE UN NODO & REGISTRY DE LOS 5 TIPOS
// ═══════════════════════════════════════════════════════════════════════════════
function N8nGenericNode({ id, data, selected }: NodeProps) {
  const node = data as unknown as WorkflowNodeData;

  const isTrigger = node.nodeType === "trigger";
  const isConditional = node.nodeType === "conditional";
  const isTransform = node.nodeType === "transform";
  const isAction = node.nodeType === "action";
  const isWebhookPreview = node.nodeType === "webhookPreview";

  const isWhatsApp =
    node.integration === "whatsapp" ||
    node.label.toLowerCase().includes("whatsapp") ||
    node.label.toLowerCase().startsWith("wa ");
  const isCalendar =
    node.integration === "calendar" ||
    node.label.toLowerCase().includes("calendar") ||
    node.label.toLowerCase().includes("calendario");
  const isTelegram =
    node.integration === "telegram" ||
    node.label.toLowerCase().includes("telegram");

  return (
    <div className="flex flex-col items-center select-none relative group">
      {/* ── CARD CUADRADA 84x84px CON SHADOW-AS-BORDER ─────────────────────── */}
      <div
        className={`w-[84px] h-[84px] rounded-[10px] bg-[#121216] relative flex items-center justify-center transition-all cursor-grab active:cursor-grabbing ${
          selected
            ? "ring-2 ring-[#b9fa01] shadow-[0_0_20px_rgba(185,250,1,0.5)] border-transparent bg-[#16161d]"
            : node.isExecuting
            ? "ring-2 ring-[#b9fa01] shadow-[0_0_16px_rgba(185,250,1,0.4)]"
            : node.isSuccess
            ? "ring-1 ring-emerald-500/80 shadow-[0_0_12px_rgba(16,185,129,0.3)]"
            : "hover:ring-1 hover:ring-white/25"
        }`}
        style={{ boxShadow: selected ? undefined : "0 0 0 1px rgba(255,255,255,0.08)" }}
      >
        {/* TOOLBAR FLOTANTE DE ACCIONES DIRECTAS EN NODO SELECCIONADO */}
        {selected && (
          <NodeToolbar
            isVisible={selected}
            position={Position.Top}
            offset={8}
            className="flex items-center gap-1.5 px-2 py-1 rounded-[6px] bg-[#0c0c10] border border-white/20 shadow-2xl backdrop-blur-md animate-in fade-in zoom-in-95 duration-150"
          >
            <span className="text-[10px] text-[#b9fa01] font-mono font-bold uppercase tracking-wider">
              {node.nodeType}
            </span>
            <div className="w-px h-3 bg-white/20" />
            <span className="text-[11px] text-white/70 font-sans">Seleccionado</span>
          </NodeToolbar>
        )}
        {/* PUERTO DE ENTRADA (A LA IZQUIERDA, SI NO ES TRIGGER) */}
        {!isTrigger && (
          <Handle
            type="target"
            position={Position.Left}
            className="!size-2 !rounded-full !border-2 !border-white/40 !bg-[#121216] hover:!bg-[#b9fa01] hover:!border-[#b9fa01] !-left-[4px] transition-colors"
          />
        )}

        {/* CONTENEDOR CENTRAL DEL ÍCONO (40x40px CON COLOR Y LOGO OFICIAL) */}
        {isWhatsApp ? (
          <div className="size-10 rounded-[8px] bg-[#25D366]/15 border border-[#25D366]/30 flex items-center justify-center shadow-xs p-1">
            <WhatsAppLogo className="size-7 shrink-0" />
          </div>
        ) : isCalendar ? (
          <div className="size-10 rounded-[8px] bg-white/[0.08] border border-white/15 flex items-center justify-center shadow-xs p-1">
            <GoogleCalendarLogo className="size-7 shrink-0" />
          </div>
        ) : isTelegram ? (
          <div className="size-10 rounded-[8px] bg-[#37aee2]/15 border border-[#37aee2]/30 flex items-center justify-center shadow-xs p-1">
            <TelegramLogo className="size-7 shrink-0" />
          </div>
        ) : isTransform ? (
          <div className="size-10 rounded-[8px] bg-[#1a1a22] text-[#b9fa01] border border-white/[0.06] flex items-center justify-center font-mono font-bold text-base shadow-xs">
            {"{}"}
          </div>
        ) : isConditional ? (
          <div className="size-10 rounded-[8px] bg-emerald-600/25 text-emerald-400 border border-emerald-500/30 flex items-center justify-center shadow-xs">
            <GitBranch className="size-5" />
          </div>
        ) : isAction ? (
          <div className="size-10 rounded-[8px] bg-indigo-600/25 text-indigo-300 border border-indigo-500/30 flex items-center justify-center shadow-xs">
            <Globe className="size-5" />
          </div>
        ) : isWebhookPreview ? (
          <div className="size-10 rounded-[8px] bg-[#1a1a24] border border-white/10 flex flex-col items-center justify-center gap-1 p-1 overflow-hidden">
            <div className="w-full h-2 rounded-xs bg-white/20" />
            <div className="w-2/3 h-1.5 rounded-xs bg-[#b9fa01]/50 self-start" />
          </div>
        ) : (
          <div className="size-10 rounded-[8px] bg-white/10 flex items-center justify-center">
            <Globe className="size-5 text-white/70" />
          </div>
        )}

        {/* PUERTOS DE SALIDA A LA DERECHA */}
        {!isConditional ? (
          <Handle
            type="source"
            position={Position.Right}
            className="!size-2 !rounded-full !border-2 !border-white/40 !bg-[#121216] hover:!bg-[#b9fa01] hover:!border-[#b9fa01] !-right-[4px] transition-colors"
          />
        ) : (
          /* NODO CONDICIONAL: DOS PUERTOS APILADOS CON ETIQUETAS */
          <>
            {/* PUERTO SUPERIOR: VERDADERO */}
            <div className="absolute -right-1 top-4 flex items-center">
              <Handle
                id="true"
                type="source"
                position={Position.Right}
                className="!size-2 !rounded-full !border-2 !border-white/40 !bg-[#121216] hover:!bg-[#b9fa01] hover:!border-[#b9fa01] !static"
              />
              <span className="text-[10px] text-white/50 font-mono ml-1.5 pointer-events-none">
                verdadero
              </span>
            </div>

            {/* PUERTO INFERIOR: FALSO */}
            <div className="absolute -right-1 bottom-4 flex items-center">
              <Handle
                id="false"
                type="source"
                position={Position.Right}
                className="!size-2 !rounded-full !border-2 !border-white/40 !bg-[#121216] hover:!bg-[#b9fa01] hover:!border-[#b9fa01] !static"
              />
              <span className="text-[10px] text-white/50 font-mono ml-1.5 pointer-events-none">
                FALSO
              </span>
            </div>
          </>
        )}
      </div>

      {/* ── TÍTULO Y SUBTÍTULO FUERA DE LA CAJA (SECCIÓN 7) ───────────────── */}
      <div className="mt-2 text-center max-w-[130px] pointer-events-none">
        <h4 className="text-[13px] font-semibold text-white leading-tight line-clamp-2">
          {node.label}
        </h4>
        {node.subtitle && (
          <p className="text-[11px] text-white/50 truncate mt-0.5 leading-tight font-mono">
            {node.subtitle}
          </p>
        )}
      </div>
    </div>
  );
}

const nodeTypes = {
  genericNode: N8nGenericNode,
};

// ═══════════════════════════════════════════════════════════════════════════════
// VISTA INTERIOR DEL FLUJO (CANVAS DE NODOS N8N)
// ═══════════════════════════════════════════════════════════════════════════════
function WorkflowCanvasInteriorView({
  flow,
  onBack,
  interiorTab,
  setInteriorTab,
}: {
  flow: FlowItem;
  onBack: () => void;
  interiorTab: InteriorTabKey;
  setInteriorTab: (tab: InteriorTabKey) => void;
}) {
  const canvasContainerRef = React.useRef<HTMLDivElement>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const { zoomIn, zoomOut, fitView } = useReactFlow();

  // NODOS CON COORDENADAS LIMPIAS Y ESPACIADAS
  const initialNodes: WorkflowNode[] = useMemo(() => {
    if (flow.id === "wf-1" || flow.tags.includes("Google Calendar")) {
      return [
        {
          id: "node-1",
          type: "genericNode",
          position: { x: 100, y: 240 },
          data: {
            label: "Widget Web 2D",
            subtitle: "POST /v1/chat/agendar",
            nodeType: "trigger",
          },
        },
        {
          id: "node-2",
          type: "genericNode",
          position: { x: 340, y: 240 },
          data: {
            label: "Normalizar Cita",
            subtitle: "Validación de slots",
            nodeType: "transform",
          },
        },
        {
          id: "node-3",
          type: "genericNode",
          position: { x: 580, y: 240 },
          data: {
            label: "¿Slot Disponible?",
            subtitle: "Filtro de colisiones",
            nodeType: "conditional",
          },
        },
        {
          id: "node-4",
          type: "genericNode",
          position: { x: 880, y: 150 },
          data: {
            label: "Google Calendar",
            subtitle: "events.insert (Confirmado)",
            nodeType: "action",
            integration: "calendar",
          },
        },
        {
          id: "node-5",
          type: "genericNode",
          position: { x: 880, y: 340 },
          data: {
            label: "Alerta WhatsApp Dueño",
            subtitle: "+57 324 369 9856",
            nodeType: "action",
            integration: "whatsapp",
          },
        },
      ];
    }
    return [
      {
        id: "node-1",
        type: "genericNode",
        position: { x: 100, y: 240 },
        data: {
          label: "Sitio Web 2D",
          subtitle: "POST /v1/webhook",
          nodeType: "trigger",
        },
      },
      {
        id: "node-2",
        type: "genericNode",
        position: { x: 340, y: 240 },
        data: {
          label: "Normalizar Canal",
          subtitle: "Limpieza de payload",
          nodeType: "transform",
        },
      },
      {
        id: "node-3",
        type: "genericNode",
        position: { x: 580, y: 240 },
        data: {
          label: "¿Es WhatsApp?",
          subtitle: "Filtro de remitente",
          nodeType: "conditional",
        },
      },
      {
        id: "node-4",
        type: "genericNode",
        position: { x: 880, y: 150 },
        data: {
          label: "Alerta WhatsApp Dueño",
          subtitle: "+57 324 369 9856",
          nodeType: "action",
          integration: "whatsapp",
        },
      },
      {
        id: "node-5",
        type: "genericNode",
        position: { x: 880, y: 340 },
        data: {
          label: "Google Calendar",
          subtitle: "Verificación de agenda",
          nodeType: "action",
          integration: "calendar",
        },
      },
    ];
  }, [flow]);

  // WIRES / EDGES BEZIER LIMPIOS
  const initialEdges = useMemo<Edge[]>(
    () => [
      {
        id: "e1-2",
        source: "node-1",
        target: "node-2",
        style: { stroke: "rgba(255, 255, 255, 0.25)", strokeWidth: 1.5 },
      },
      {
        id: "e2-3",
        source: "node-2",
        target: "node-3",
        style: { stroke: "rgba(255, 255, 255, 0.25)", strokeWidth: 1.5 },
      },
      {
        id: "e3-4",
        source: "node-3",
        sourceHandle: "true",
        target: "node-4",
        style: { stroke: "rgba(255, 255, 255, 0.25)", strokeWidth: 1.5 },
      },
      {
        id: "e3-5",
        source: "node-3",
        sourceHandle: "false",
        target: "node-5",
        style: { stroke: "rgba(255, 255, 255, 0.25)", strokeWidth: 1.5 },
      },
    ],
    []
  );

  // Estados interactivos nativos de React Flow (Drag, Select, Connect, Delete)
  const [nodes, setNodes, onNodesChange] = useNodesState<WorkflowNode>(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>(initialEdges);

  // Conectar nodos arrastrando desde puertos
  const onConnect: OnConnect = useCallback(
    (params) =>
      setEdges((eds) =>
        addEdge(
          {
            ...params,
            style: { stroke: "rgba(255, 255, 255, 0.25)", strokeWidth: 1.5 },
          },
          eds
        )
      ),
    [setEdges]
  );

  // Nodo seleccionado actualmente para edición / renombrado / borrado
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const selectedNode = useMemo(
    () => nodes.find((n) => n.id === selectedNodeId) || null,
    [nodes, selectedNodeId]
  );

  // Renombrar nodo
  const handleRenameNode = (newLabel: string) => {
    setNodes((nds) =>
      nds.map((n) =>
        n.id === selectedNodeId
          ? { ...n, data: { ...n.data, label: newLabel } }
          : n
      )
    );
  };

  // Editar subtítulo o endpoint
  const handleUpdateSubtitle = (newSub: string) => {
    setNodes((nds) =>
      nds.map((n) =>
        n.id === selectedNodeId
          ? { ...n, data: { ...n.data, subtitle: newSub } }
          : n
      )
    );
  };

  // Duplicar nodo seleccionado
  const handleDuplicateNode = (nodeToDup?: WorkflowNode) => {
    const target = nodeToDup || selectedNode;
    if (!target) return;
    const newNode: WorkflowNode = {
      ...target,
      id: `node-${Date.now()}`,
      position: { x: target.position.x + 50, y: target.position.y + 50 },
      data: { ...target.data, label: `${target.data.label} (Copia)` },
      selected: true,
    };
    setNodes((nds) => [...nds.map((n) => ({ ...n, selected: false })), newNode]);
    setSelectedNodeId(newNode.id);
  };

  // Borrar nodo seleccionado
  const handleDeleteNode = (idToDelete?: string) => {
    const targetId = idToDelete || selectedNodeId;
    if (!targetId) return;
    setNodes((nds) => nds.filter((n) => n.id !== targetId));
    setEdges((eds) => eds.filter((e) => e.source !== targetId && e.target !== targetId));
    if (selectedNodeId === targetId) setSelectedNodeId(null);
  };

  // Poner pantalla grande (Fullscreen)
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      canvasContainerRef.current?.requestFullscreen?.();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen?.();
      setIsFullscreen(false);
    }
  };

  // Ejecuciones de muestra para la pestaña "Ejecuciones"
  const workflowExecutions = useMemo(
    () => [
      { id: "exec-1048", status: "Completado", startTime: "Hace 12 min", duration: "410ms" },
      { id: "exec-1047", status: "Completado", startTime: "Hace 45 min", duration: "385ms" },
      { id: "exec-1046", status: "Completado", startTime: "Hace 2 horas", duration: "520ms" },
      { id: "exec-1045", status: "Completado", startTime: "Ayer 18:30", duration: "490ms" },
    ],
    []
  );

  return (
    <div
      ref={canvasContainerRef}
      className="relative w-full h-[calc(100vh-4rem)] bg-[#000000] text-white overflow-hidden select-none font-sans"
    >
      {/* ── CONTROLES MÓVIL (BOTÓN VOLVER + TABS COMPACTAS) ── */}
      <div className="md:hidden absolute top-4 left-4 z-30 flex items-center gap-1.5">
        <button
          type="button"
          onClick={onBack}
          className="flex items-center gap-1 px-2.5 py-1.5 rounded-[6px] bg-[#0c0c10]/95 border border-white/10 text-white/80 hover:text-white text-[12px] font-medium backdrop-blur-md cursor-pointer shadow-lg"
          title="Volver a lista de flujos"
        >
          <ChevronLeft className="size-3.5" />
          <span>Flujos</span>
        </button>
        <div className="flex items-center p-0.5 rounded-[6px] bg-[#0c0c10]/95 border border-white/10 backdrop-blur-md shadow-lg">
          <button
            type="button"
            onClick={() => setInteriorTab("editor")}
            className={`px-2 py-1 rounded-[4px] text-[11px] font-medium transition-all cursor-pointer ${
              interiorTab === "editor"
                ? "bg-white text-black font-semibold"
                : "text-white/50"
            }`}
          >
            Editor
          </button>
          <button
            type="button"
            onClick={() => setInteriorTab("ejecuciones")}
            className={`px-2 py-1 rounded-[4px] text-[11px] font-medium transition-all cursor-pointer ${
              interiorTab === "ejecuciones"
                ? "bg-white text-black font-semibold"
                : "text-white/50"
            }`}
          >
            Ejec.
          </button>
        </div>
      </div>

      {/* ── CONTROLES DE PANTALLA Y VISTA (PANTALLA GRANDE / ZOOM / CENTRAR) ── */}
      {interiorTab === "editor" && (
        <div className="absolute top-4 right-4 sm:top-6 sm:right-6 z-30 flex items-center gap-1 p-1 rounded-[8px] bg-[#0c0c10]/95 border border-white/[0.08] shadow-2xl backdrop-blur-md">
          <button
            type="button"
            onClick={() => fitView({ duration: 300 })}
            className="p-1.5 rounded-[6px] text-white/50 hover:text-white hover:bg-white/[0.08] transition-colors cursor-pointer"
            title="Centrar y ajustar lienzo"
          >
            <RotateCcw className="size-4" />
          </button>
          <button
            type="button"
            onClick={() => zoomIn({ duration: 250 })}
            className="p-1.5 rounded-[6px] text-white/50 hover:text-white hover:bg-white/[0.08] transition-colors cursor-pointer"
            title="Acercar (+)"
          >
            <ZoomIn className="size-4" />
          </button>
          <button
            type="button"
            onClick={() => zoomOut({ duration: 250 })}
            className="p-1.5 rounded-[6px] text-white/50 hover:text-white hover:bg-white/[0.08] transition-colors cursor-pointer"
            title="Alejar (-)"
          >
            <ZoomOut className="size-4" />
          </button>
          <div className="w-px h-3.5 bg-white/10 mx-0.5" />
          <button
            type="button"
            onClick={toggleFullscreen}
            className="p-1.5 px-2 rounded-[6px] text-white/70 hover:text-white hover:bg-white/[0.08] transition-colors cursor-pointer flex items-center gap-1.5 text-[12px] font-medium"
            title={isFullscreen ? "Salir de pantalla completa" : "Poner pantalla grande"}
          >
            {isFullscreen ? (
              <Minimize2 className="size-4 text-[#b9fa01]" />
            ) : (
              <Maximize2 className="size-4" />
            )}
            <span className="hidden sm:inline text-xs">
              {isFullscreen ? "Reducir" : "Pantalla grande"}
            </span>
          </button>
        </div>
      )}

      {/* ── VISTA: EDITOR (CANVAS DE NODOS 100% INTERACTIVO Y EDITABLE) ──── */}
      {interiorTab === "editor" && (
        <div className="w-full h-full">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            nodesDraggable={true}
            nodesConnectable={true}
            elementsSelectable={true}
            deleteKeyCode={["Backspace", "Delete"]}
            onNodeClick={(_, node) => setSelectedNodeId(node.id)}
            onPaneClick={() => setSelectedNodeId(null)}
            panOnDrag={true}
            zoomOnScroll={true}
            minZoom={0.25}
            maxZoom={2}
            fitView
            defaultViewport={{ x: 100, y: 100, zoom: 0.9 }}
            className="bg-[#000000]"
          >
            {/* PATRÓN DE PUNTOS DOT-GRID SUTIL */}
            <Background
              variant={BackgroundVariant.Dots}
              gap={20}
              size={1.2}
              color="#222228"
              className="opacity-80"
            />
          </ReactFlow>

          {/* ── PANEL LATERAL (DRAWER): INSPECTOR Y EDICIÓN DEL NODO SELECCIONADO ── */}
          {selectedNode && (
            <div className="absolute top-0 right-0 bottom-0 w-80 sm:w-88 bg-[#0c0c10] border-l border-white/[0.08] shadow-2xl z-40 flex flex-col justify-between p-6 animate-in slide-in-from-right duration-200">
              <div className="space-y-6">
                {/* Cabecera del panel */}
                <div className="flex items-center justify-between pb-4 border-b border-white/[0.06]">
                  <div className="flex items-center gap-3">
                    <div className="size-9 rounded-[8px] bg-white/[0.06] border border-white/10 flex items-center justify-center p-1.5 shadow-xs">
                      {selectedNode.data.integration === "calendar" ||
                      selectedNode.data.label.toLowerCase().includes("calendar") ? (
                        <GoogleCalendarLogo className="size-5 shrink-0" />
                      ) : selectedNode.data.integration === "whatsapp" ||
                        selectedNode.data.label.toLowerCase().includes("whatsapp") ? (
                        <WhatsAppLogo className="size-5 shrink-0" />
                      ) : (
                        <Globe className="size-4 text-white/70" />
                      )}
                    </div>
                    <div className="min-w-0">
                      <span className="text-[10px] font-mono uppercase text-[#b9fa01] tracking-wider block">
                        {selectedNode.data.nodeType}
                      </span>
                      <h3 className="text-sm font-semibold text-white truncate max-w-[160px]">
                        {selectedNode.data.label}
                      </h3>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => setSelectedNodeId(null)}
                    className="size-7 rounded-md hover:bg-white/[0.08] text-white/40 hover:text-white flex items-center justify-center cursor-pointer transition-colors"
                    title="Cerrar panel"
                  >
                    <X className="size-4" />
                  </button>
                </div>

                {/* Formulario de Renombrado y Parámetros */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-[11px] font-mono uppercase tracking-wider text-white/50 mb-1.5">
                      Nombre del nodo
                    </label>
                    <input
                      type="text"
                      value={selectedNode.data.label}
                      onChange={(e) => handleRenameNode(e.target.value)}
                      className="w-full px-3 py-2 rounded-[6px] bg-[#141418] border border-white/10 text-white text-[13px] font-medium focus:border-[#b9fa01] focus:outline-hidden focus:ring-1 focus:ring-[#b9fa01] transition-all"
                      placeholder="Nombre del nodo..."
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-mono uppercase tracking-wider text-white/50 mb-1.5">
                      Subtítulo / Parámetro
                    </label>
                    <input
                      type="text"
                      value={selectedNode.data.subtitle || ""}
                      onChange={(e) => handleUpdateSubtitle(e.target.value)}
                      className="w-full px-3 py-2 rounded-[6px] bg-[#141418] border border-white/10 text-white/80 text-[13px] font-mono focus:border-[#b9fa01] focus:outline-hidden focus:ring-1 focus:ring-[#b9fa01] transition-all"
                      placeholder="POST /v1/action"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-mono uppercase tracking-wider text-white/50 mb-1.5">
                      ID del nodo
                    </label>
                    <div className="px-3 py-2 rounded-[6px] bg-[#141418]/60 border border-white/[0.06] text-white/40 font-mono text-[12px] select-all truncate">
                      {selectedNode.id}
                    </div>
                  </div>
                </div>
              </div>

              {/* Botones de acción del nodo: Duplicar y Borrar */}
              <div className="pt-6 border-t border-white/[0.06] flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => handleDuplicateNode(selectedNode)}
                  className="flex-1 py-2 px-3 rounded-[6px] bg-white/[0.06] hover:bg-white/[0.1] text-white text-[12px] font-semibold flex items-center justify-center gap-1.5 transition-colors cursor-pointer"
                >
                  <Copy className="size-3.5" />
                  <span>Duplicar</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleDeleteNode(selectedNode.id)}
                  className="py-2 px-3 rounded-[6px] border border-red-500/30 text-red-400 hover:bg-red-500/10 text-[12px] font-semibold flex items-center justify-center gap-1.5 transition-colors cursor-pointer"
                >
                  <Trash2 className="size-3.5" />
                  <span>Borrar</span>
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── VISTA: EJECUCIONES ────────────────────────────────────────── */}
      {interiorTab === "ejecuciones" && (
        <div className="w-full h-full bg-[#000000] p-8 overflow-y-auto">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-[18px] font-semibold text-white tracking-tight mb-1">
              Ejecuciones de este flujo
            </h2>
            <p className="text-[13px] text-white/50 mb-6">
              Historial de ejecuciones registradas automáticamente en tiempo real
            </p>

            <div className="rounded-[8px] border border-white/[0.08] bg-[#070709] overflow-hidden">
              <table className="w-full text-left text-[13px]">
                <thead className="bg-[#0e0e12] text-white/40 border-b border-white/[0.06] font-mono text-[11px] uppercase tracking-wider">
                  <tr>
                    <th className="py-3 px-4">Estado</th>
                    <th className="py-3 px-4">ID Ejecución</th>
                    <th className="py-3 px-4">Inicio</th>
                    <th className="py-3 px-4">Duración</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/[0.04]">
                  {workflowExecutions.map((item) => (
                    <tr key={item.id} className="hover:bg-white/[0.02] transition-colors">
                      <td className="py-3 px-4">
                        <span className="inline-flex items-center gap-1.5 text-emerald-400 font-medium text-[12px]">
                          <span className="size-1.5 rounded-full bg-emerald-400" />
                          {item.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-mono text-white/70">{item.id}</td>
                      <td className="py-3 px-4 text-white/50">{item.startTime}</td>
                      <td className="py-3 px-4 font-mono text-white/50">{item.duration}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ── VISTA: EVALUACIONES ───────────────────────────────────────── */}
      {interiorTab === "evaluaciones" && (
        <div className="w-full h-full bg-[#000000] flex items-center justify-center p-8">
          <div className="text-center max-w-sm">
            <p className="text-[15px] font-medium text-white/80">
              Sin evaluaciones configuradas
            </p>
            <p className="text-[13px] text-white/40 mt-1">
              Las evaluaciones automáticas permiten medir precisión de respuestas y tiempos de resolución.
            </p>
          </div>
        </div>
      )}

    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// COMPONENTE PRINCIPAL QUE GESTIONA LA LISTA Y EL DETALLE INTERIOR
// ═══════════════════════════════════════════════════════════════════════════════
export default function FlujosSubpage() {
  const [activeTab, setActiveTab] = useState<TabKey>("flujos");
  const [flows, setFlows] = useState<FlowItem[]>(INITIAL_FLOWS);
  const [selectedFlowIds, setSelectedFlowIds] = useState<string[]>([]);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  // Filtros de Credenciales (Patrón C)
  const [searchCred, setSearchCred] = useState("");
  const [credSort, setCredSort] = useState<"name" | "recent">("name");

  // Estado del flujo abierto para ver su interior quirúrgico (por defecto el lienzo n8n del flujo activo)
  const [openedFlow, setOpenedFlow] = useState<FlowItem | null>(INITIAL_FLOWS[0]);
  const [interiorTab, setInteriorTab] = useState<InteriorTabKey>("editor");

  // Estados de control total (Kebab menu, modales y acciones en lote)
  const [menuOpenFlowId, setMenuOpenFlowId] = useState<string | null>(null);
  const [renameModalFlow, setRenameModalFlow] = useState<FlowItem | null>(null);
  const [renameName, setRenameName] = useState("");
  const [renameDesc, setRenameDesc] = useState("");
  const [deleteConfirmFlowIds, setDeleteConfirmFlowIds] = useState<string[] | null>(null);

  // Generador de flujos por lenguaje natural (Nova / Automation Architect)
  const [isAiModalOpen, setIsAiModalOpen] = useState(false);
  const [aiPrompt, setAiPrompt] = useState("");
  const [isGeneratingFlow, setIsGeneratingFlow] = useState(false);
  const [aiGenError, setAiGenError] = useState("");

  const handleGenerateWorkflowWithAI = async () => {
    if (!aiPrompt.trim()) return;
    setIsGeneratingFlow(true);
    setAiGenError("");
    try {
      const res = await fetch("/api/workspace/workflows/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description: aiPrompt, clinic_name: "Firby" })
      });
      const data = await res.json();
      if (data.ok) {
        const newWf: FlowItem = {
          id: data.workflow_id || `wf-${Date.now()}`,
          name: data.name || "Nuevo flujo generado por Nova",
          description: aiPrompt,
          status: "Publicado",
          lastRun: "Recién creado",
          createdBy: "Nova (AI Architect)",
          triggerType: "Webhook Receptor",
          tags: ["Automatización AI", "n8n"]
        };
        setFlows((prev) => [newWf, ...prev]);
        setIsAiModalOpen(false);
        setAiPrompt("");
        setOpenedFlow(newWf);
      } else {
        setAiGenError(data.error || "No se pudo generar el flujo.");
      }
    } catch (e: any) {
      setAiGenError(e.message || "Error al conectar con el motor de automatizaciones.");
    } finally {
      setIsGeneratingFlow(false);
    }
  };

  // Acciones individuales
  const handleDuplicateFlow = (flow: FlowItem) => {
    const duplicated: FlowItem = {
      ...flow,
      id: `wf-${Date.now()}`,
      name: `${flow.name} (Copia)`,
      lastRun: "Nunca",
      status: "Borrador",
    };
    setFlows((prev) => [duplicated, ...prev]);
    setMenuOpenFlowId(null);
  };

  const handleToggleStatus = (id: string) => {
    setFlows((prev) =>
      prev.map((f) =>
        f.id === id
          ? { ...f, status: f.status === "Publicado" ? "Pausado" : "Publicado" }
          : f
      )
    );
    setMenuOpenFlowId(null);
  };

  const handleExportJSON = (flow: FlowItem) => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(flow, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `${flow.name.toLowerCase().replace(/[^a-z0-9]/g, "_")}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
    setMenuOpenFlowId(null);
  };

  // Acciones en masa (Bulk actions)
  const handleBulkPublish = () => {
    setFlows((prev) =>
      prev.map((f) => (selectedFlowIds.includes(f.id) ? { ...f, status: "Publicado" } : f))
    );
  };

  const handleBulkPause = () => {
    setFlows((prev) =>
      prev.map((f) => (selectedFlowIds.includes(f.id) ? { ...f, status: "Pausado" } : f))
    );
  };

  const handleBulkDuplicate = () => {
    const duplicates: FlowItem[] = flows
      .filter((f) => selectedFlowIds.includes(f.id))
      .map((f) => ({
        ...f,
        id: `wf-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
        name: `${f.name} (Copia)`,
        lastRun: "Nunca",
        status: "Borrador",
      }));
    setFlows((prev) => [...duplicates, ...prev]);
    setSelectedFlowIds([]);
  };

  const handleBulkExportJSON = () => {
    const selected = flows.filter((f) => selectedFlowIds.includes(f.id));
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(selected, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `flujos_firby_export_${Date.now()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const handleBulkDelete = () => {
    setDeleteConfirmFlowIds(selectedFlowIds);
  };

  const handleConfirmDelete = () => {
    if (!deleteConfirmFlowIds) return;
    setFlows((prev) => prev.filter((f) => !deleteConfirmFlowIds.includes(f.id)));
    setSelectedFlowIds((prev) => prev.filter((id) => !deleteConfirmFlowIds.includes(id)));
    setDeleteConfirmFlowIds(null);
    setMenuOpenFlowId(null);
  };

  // Selección de filas
  const isAllSelected = flows.length > 0 && selectedFlowIds.length === flows.length;
  const toggleSelectAll = () => {
    if (isAllSelected) {
      setSelectedFlowIds([]);
    } else {
      setSelectedFlowIds(flows.map((f) => f.id));
    }
  };

  const toggleSelectRow = (id: string) => {
    setSelectedFlowIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const handleCreateFlow = () => {
    const newFlow: FlowItem = {
      id: `wf-${Date.now()}`,
      name: "Nuevo Flujo de Automatización",
      description: "Automatización personalizada de atención y citas",
      status: "Publicado",
      lastRun: "Recién creado",
      createdBy: "Santiago Rubio",
      triggerType: "Sitio Web 2D",
      tags: ["Nuevo"],
    };
    setFlows((prev) => [newFlow, ...prev]);
    setOpenedFlow(newFlow);
    setIsDropdownOpen(false);
  };

  const filteredCredentials = useMemo(() => {
    return INITIAL_CREDENTIALS.filter(
      (c) =>
        c.name.toLowerCase().includes(searchCred.toLowerCase()) ||
        c.service.toLowerCase().includes(searchCred.toLowerCase())
    ).sort((a, b) => {
      if (credSort === "name") return a.name.localeCompare(b.name);
      return 0;
    });
  }, [searchCred, credSort]);

  // Si el usuario abrió un flujo ➔ Renderiza la VISTA INTERIOR QUIRÚRGICA
  if (openedFlow) {
    return (
      <AppShell
        fullWidth={true}
        noPadding={true}
        headerSlot={
          <div className="flex items-center gap-3 lg:gap-4 text-[13px] select-none">
            {/* SECCIÓN / BREADCRUMB (SIN 'PUBLICADO') */}
            <div className="flex items-center gap-1.5 sm:gap-2">
              <button
                type="button"
                onClick={() => {
                  setOpenedFlow(null);
                  setInteriorTab("editor");
                }}
                className="text-white/40 hover:text-white transition-colors cursor-pointer font-medium text-xs sm:text-[13px]"
                title="Volver a la lista de flujos"
              >
                Personal
              </button>
              <span className="text-white/20 text-[11px]">›</span>
              <span className="text-white font-medium truncate max-w-[140px] sm:max-w-[200px] lg:max-w-[300px] text-xs sm:text-[13px]">
                {openedFlow.name}
              </span>
            </div>

            {/* SEPARADOR VERTICAL */}
            <div className="w-px h-4 bg-white/10 shrink-0" />

            {/* PESTAÑAS ARRIBA AL LADO DE LAS SECCIONES */}
            <div className="flex items-center p-0.5 rounded-[7px] bg-[#121216] border border-white/[0.08] shrink-0">
              <button
                type="button"
                onClick={() => setInteriorTab("editor")}
                className={`px-2.5 sm:px-3 py-1 rounded-[5px] text-[11px] sm:text-[12px] font-medium transition-all cursor-pointer ${
                  interiorTab === "editor"
                    ? "bg-white text-black font-semibold shadow-xs"
                    : "text-white/50 hover:text-white"
                }`}
              >
                Editor
              </button>
              <button
                type="button"
                onClick={() => setInteriorTab("ejecuciones")}
                className={`px-2.5 sm:px-3 py-1 rounded-[5px] text-[11px] sm:text-[12px] font-medium transition-all cursor-pointer ${
                  interiorTab === "ejecuciones"
                    ? "bg-white text-black font-semibold shadow-xs"
                    : "text-white/50 hover:text-white"
                }`}
              >
                Ejecuciones
              </button>
              <button
                type="button"
                onClick={() => setInteriorTab("evaluaciones")}
                className={`px-2.5 sm:px-3 py-1 rounded-[5px] text-[11px] sm:text-[12px] font-medium transition-all cursor-pointer ${
                  interiorTab === "evaluaciones"
                    ? "bg-white text-black font-semibold shadow-xs"
                    : "text-white/50 hover:text-white"
                }`}
              >
                Evaluaciones
              </button>
            </div>
          </div>
        }
      >
        <ReactFlowProvider>
          <WorkflowCanvasInteriorView
            flow={openedFlow}
            interiorTab={interiorTab}
            setInteriorTab={setInteriorTab}
            onBack={() => {
              setOpenedFlow(null);
              setInteriorTab("editor");
            }}
          />
        </ReactFlowProvider>
      </AppShell>
    );
  }

  // ═════════════════════════════════════════════════════════════════════════════
  // SHELL ADMINISTRATIVO: LISTA PRINCIPAL
  // ═════════════════════════════════════════════════════════════════════════════
  return (
    <AppShell fullWidth={true} noPadding={true}>
      <div className="w-full min-h-[calc(100vh-4rem)] bg-[#000000] text-white px-4 sm:px-8 pt-6 sm:pt-8 pb-16 font-sans select-none overflow-y-auto">
        
        {/* ── 2. HEADER DE PÁGINA ─────────────────────────────────────────── */}
        <header className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          {/* BLOQUE IZQUIERDO */}
          <div className="flex flex-col gap-1">
            <h1 className="text-[22px] font-semibold text-white tracking-tight leading-tight">
              Flujos
            </h1>
            <p className="text-[13px] font-normal text-white/50">
              Todos los flujos de automatización activos en tu cuenta
            </p>
          </div>

          {/* BLOQUE DERECHO: SPLIT BUTTON COMPUESTO */}
          <div className="relative inline-flex items-stretch shrink-0 shadow-xs">
            <button
              type="button"
              onClick={handleCreateFlow}
              className="h-9 px-4 rounded-l-[6px] rounded-r-none bg-[#b9fa01] hover:bg-[#a5e000] text-black text-[13px] font-semibold transition-colors cursor-pointer flex items-center justify-center tracking-tight"
            >
              Crear flujo
            </button>

            <button
              type="button"
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="h-9 w-8 rounded-r-[6px] rounded-l-none bg-[#b9fa01] hover:bg-[#a5e000] text-black border-l border-black/20 transition-colors cursor-pointer flex items-center justify-center"
              title="Opciones de creación"
              aria-label="Opciones de creación"
            >
              <ChevronDown className="size-4" />
            </button>

            {/* DROPDOWN MENU */}
            {isDropdownOpen && (
              <div className="absolute right-0 top-11 w-52 bg-[#0c0c10] border border-white/[0.08] rounded-[8px] p-1.5 shadow-2xl z-50 text-[13px]">
                <button
                  type="button"
                  onClick={handleCreateFlow}
                  className="w-full text-left px-3 py-2 rounded-[5px] text-white hover:bg-white/[0.06] transition-colors cursor-pointer"
                >
                  Flujo en blanco
                </button>
                <button
                  type="button"
                  onClick={handleCreateFlow}
                  className="w-full text-left px-3 py-2 rounded-[5px] text-white hover:bg-white/[0.06] transition-colors cursor-pointer"
                >
                  Desde plantilla oficial
                </button>
                <button
                  type="button"
                  onClick={handleCreateFlow}
                  className="w-full text-left px-3 py-2 rounded-[5px] text-neutral-400 hover:text-white hover:bg-white/[0.06] transition-colors cursor-pointer"
                >
                  Importar JSON
                </button>
                <div className="h-px bg-white/[0.08] my-1" />
                <button
                  type="button"
                  onClick={() => {
                    setIsDropdownOpen(false);
                    setIsAiModalOpen(true);
                  }}
                  className="w-full text-left px-3 py-2 rounded-[5px] text-[#b9fa01] hover:bg-white/[0.06] transition-colors cursor-pointer font-medium flex items-center justify-between"
                >
                  <span>Generar con IA (Nova)</span>
                  <Sparkles className="size-3.5" />
                </button>
              </div>
            )}
          </div>
        </header>

        {/* MODAL GENERADOR DE FLUJOS POR IA (NOVA / AUTOMATION ARCHITECT) */}
        {isAiModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-xs p-4">
            <div className="bg-[#0c0c10] border border-white/10 rounded-2xl w-full max-w-lg p-6 space-y-5 shadow-2xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded-lg bg-[#b9fa01]/10 text-[#b9fa01]">
                    <Sparkles className="size-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white">Generar Flujo con Lenguaje Natural</h3>
                    <p className="text-[11px] text-neutral-400">Nova traducirá tu idea a un grafo ejecutable en n8n.</p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setIsAiModalOpen(false)}
                  className="text-neutral-400 hover:text-white cursor-pointer"
                >
                  <X className="size-4" />
                </button>
              </div>

              <div className="space-y-2">
                <label className="text-[11px] font-semibold text-neutral-300">
                  ¿Qué debe hacer esta automatización?
                </label>
                <textarea
                  value={aiPrompt}
                  onChange={(e) => setAiPrompt(e.target.value)}
                  placeholder="Ejemplo: Cada vez que un paciente agende una cita, envía un correo de confirmación al doctor y guarda los datos en Google Sheets..."
                  rows={4}
                  className="w-full p-3.5 rounded-xl bg-white/[0.04] border border-white/10 text-xs text-white placeholder-neutral-500 focus:outline-hidden focus:ring-1 focus:ring-[#b9fa01] leading-relaxed"
                />
              </div>

              {aiGenError && (
                <div className="p-3 rounded-lg bg-red-950/50 border border-red-900 text-xs text-red-300">
                  {aiGenError}
                </div>
              )}

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsAiModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-neutral-400 hover:text-white transition-colors cursor-pointer"
                >
                  Cancelar
                </button>
                <button
                  type="button"
                  onClick={handleGenerateWorkflowWithAI}
                  disabled={isGeneratingFlow || !aiPrompt.trim()}
                  className="px-5 py-2 rounded-xl text-xs font-semibold bg-[#b9fa01] hover:bg-[#a5e000] text-black transition-colors cursor-pointer flex items-center gap-1.5 shadow-xs"
                >
                  {isGeneratingFlow ? "Generando en n8n..." : "Construir Flujo"}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ── 3. FILA DE STAT CARDS (KPI ROW) ─────────────────────────────── */}
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mt-6">
          <div
            className="bg-[#070709] rounded-[10px] p-4 flex flex-col justify-between gap-2"
            style={{ boxShadow: "0 0 0 1px rgba(255,255,255,0.06)" }}
          >
            <span className="text-[12px] font-normal text-white/50">
              Flujos publicados
            </span>
            <span className="text-[26px] font-semibold text-white tabular-nums leading-none">
              3
            </span>
          </div>

          <div
            className="bg-[#070709] rounded-[10px] p-4 flex flex-col justify-between gap-2"
            style={{ boxShadow: "0 0 0 1px rgba(255,255,255,0.06)" }}
          >
            <span className="text-[12px] font-normal text-white/50">
              Flujos con errores
            </span>
            <span className="text-[26px] font-semibold text-white tabular-nums leading-none">
              0
            </span>
          </div>

          <div
            className="bg-[#070709] rounded-[10px] p-4 flex flex-col justify-between gap-2"
            style={{ boxShadow: "0 0 0 1px rgba(255,255,255,0.06)" }}
          >
            <span className="text-[12px] font-normal text-white/50">
              Tasa de éxito
            </span>
            <span className="text-[26px] font-semibold text-white tabular-nums leading-none">
              100%
            </span>
          </div>

          <div
            className="bg-[#070709] rounded-[10px] p-4 flex flex-col justify-between gap-2"
            style={{ boxShadow: "0 0 0 1px rgba(255,255,255,0.06)" }}
          >
            <span className="text-[12px] font-normal text-white/50">
              Tiempo ahorrado
            </span>
            <div className="flex items-center justify-between">
              <span className="text-[26px] font-semibold text-white tabular-nums leading-none">
                42h
              </span>
              <svg className="size-5 shrink-0 -rotate-90" viewBox="0 0 24 24">
                <circle
                  cx="12"
                  cy="12"
                  r="9"
                  stroke="rgba(255,255,255,0.08)"
                  strokeWidth="2.5"
                  fill="none"
                />
                <circle
                  cx="12"
                  cy="12"
                  r="9"
                  stroke="#b9fa01"
                  strokeWidth="2.5"
                  fill="none"
                  strokeDasharray="56.5"
                  strokeDashoffset="14"
                  strokeLinecap="round"
                />
              </svg>
            </div>
          </div>

          <div
            className="bg-[#070709] rounded-[10px] p-4 flex flex-col justify-between gap-2"
            style={{ boxShadow: "0 0 0 1px rgba(255,255,255,0.06)" }}
          >
            <span className="text-[12px] font-normal text-white/50">
              Ejecuciones/día (promedio)
            </span>
            <span className="text-[26px] font-semibold text-white tabular-nums leading-none">
              148
            </span>
          </div>
        </section>

        {/* ── 4. TAB ROW (NAVEGACIÓN SECUNDARIA) ──────────────────────────── */}
        <nav className="flex items-center gap-5 sm:gap-7 mt-6 border-b border-white/[0.06] w-full overflow-x-auto no-scrollbar">
          <button
            type="button"
            onClick={() => setActiveTab("flujos")}
            className={`py-2.5 px-1 text-[13px] font-medium transition-colors cursor-pointer shrink-0 relative ${
              activeTab === "flujos"
                ? "text-white after:absolute after:bottom-0 after:left-0 after:right-0 after:h-[2px] after:bg-[#b9fa01]"
                : "text-white/50 hover:text-white"
            }`}
          >
            Flujos
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("credenciales")}
            className={`py-2.5 px-1 text-[13px] font-medium transition-colors cursor-pointer shrink-0 relative ${
              activeTab === "credenciales"
                ? "text-white after:absolute after:bottom-0 after:left-0 after:right-0 after:h-[2px] after:bg-[#b9fa01]"
                : "text-white/50 hover:text-white"
            }`}
          >
            Credenciales
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("ejecuciones")}
            className={`py-2.5 px-1 text-[13px] font-medium transition-colors cursor-pointer shrink-0 relative ${
              activeTab === "ejecuciones"
                ? "text-white after:absolute after:bottom-0 after:left-0 after:right-0 after:h-[2px] after:bg-[#b9fa01]"
                : "text-white/50 hover:text-white"
            }`}
          >
            Ejecuciones
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("variables")}
            className={`py-2.5 px-1 text-[13px] font-medium transition-colors cursor-pointer shrink-0 relative ${
              activeTab === "variables"
                ? "text-white after:absolute after:bottom-0 after:left-0 after:right-0 after:h-[2px] after:bg-[#b9fa01]"
                : "text-white/50 hover:text-white"
            }`}
          >
            Variables
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("tablas")}
            className={`py-2.5 px-1 text-[13px] font-medium transition-colors cursor-pointer shrink-0 relative ${
              activeTab === "tablas"
                ? "text-white after:absolute after:bottom-0 after:left-0 after:right-0 after:h-[2px] after:bg-[#b9fa01]"
                : "text-white/50 hover:text-white"
            }`}
          >
            Tablas de datos
          </button>
        </nav>

        {/* ── 5. CONTENIDO POR TAB ─────────────────────────────────────────── */}

        {/* TAB 1: FLUJOS (PATRÓN A — TABLA CON DATOS) */}
        {activeTab === "flujos" && (
          <div className="mt-5">
            <div className="flex items-center justify-between">
              <label className="inline-flex items-center gap-2 cursor-pointer text-[12px] text-white/50 hover:text-white/70 transition-colors">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="size-3.5 rounded accent-[#b9fa01] cursor-pointer"
                />
                <span>Actualización automática</span>
              </label>

              <button
                type="button"
                className="p-1.5 rounded-md hover:bg-white/[0.06] text-white/50 hover:text-white transition-colors cursor-pointer"
                title="Filtrar flujos"
                aria-label="Filtrar flujos"
              >
                <Filter className="size-4" />
              </button>
            </div>

            <div
              className="mt-3 rounded-[10px] overflow-x-auto bg-[#070709]"
              style={{ boxShadow: "0 0 0 1px rgba(255,255,255,0.06)" }}
            >
              <table className="w-full text-left border-collapse min-w-[700px]">
                <thead>
                  <tr className="bg-[#0a0a0d] h-10 text-[11px] font-semibold text-white/50 tracking-[0.03em] uppercase border-b border-white/[0.06]">
                    <th className="w-12 px-4">
                      <input
                        type="checkbox"
                        checked={isAllSelected}
                        onChange={toggleSelectAll}
                        className="size-3.5 rounded accent-[#b9fa01] cursor-pointer"
                        aria-label="Seleccionar todo"
                      />
                    </th>
                    <th className="px-4 font-semibold">NOMBRE DEL FLUJO</th>
                    <th className="px-4 font-semibold">ESTADO</th>
                    <th className="px-4 font-semibold">ÚLTIMA EJECUCIÓN</th>
                    <th className="px-4 font-semibold">CREADO POR</th>
                    <th className="w-12 px-4 text-right font-semibold">ACCIONES</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/[0.04]">
                  {flows.map((flow) => {
                    const isSelected = selectedFlowIds.includes(flow.id);
                    return (
                      <tr
                        key={flow.id}
                        onClick={() => setOpenedFlow(flow)}
                        className={`h-12 text-[13px] transition-colors duration-150 cursor-pointer ${
                          isSelected ? "bg-white/[0.04]" : "hover:bg-[#0f0f13]"
                        }`}
                      >
                        <td className="w-12 px-4" onClick={(e) => e.stopPropagation()}>
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={() => toggleSelectRow(flow.id)}
                            className="size-3.5 rounded accent-[#b9fa01] cursor-pointer"
                          />
                        </td>
                        <td className="px-4 font-medium text-white hover:text-[#b9fa01] transition-colors py-2.5">
                          <div className="flex items-center gap-3">
                            {flow.tags.includes("Google Calendar") ? (
                              <div className="size-7 rounded-[6px] bg-white/[0.05] border border-white/10 flex items-center justify-center shrink-0 p-1 shadow-xs">
                                <GoogleCalendarLogo className="size-4 shrink-0" />
                              </div>
                            ) : flow.tags.includes("WhatsApp Privado") ? (
                              <div className="size-7 rounded-[6px] bg-[#25D366]/[0.08] border border-[#25D366]/20 flex items-center justify-center shrink-0 p-1 shadow-xs">
                                <WhatsAppLogo className="size-4 shrink-0" />
                              </div>
                            ) : (
                              <div className="size-7 rounded-[6px] bg-white/[0.04] border border-white/10 flex items-center justify-center shrink-0">
                                <Globe className="size-3.5 text-white/70" />
                              </div>
                            )}
                            <div className="flex flex-col min-w-0">
                              <span className="truncate font-medium">{flow.name}</span>
                              <span className="text-[11px] text-white/40 font-normal truncate">
                                {flow.description}
                              </span>
                            </div>
                          </div>
                        </td>
                        <td className="px-4">
                          <div className="inline-flex items-center gap-2">
                            <span
                              className={`size-1.5 rounded-full ${
                                flow.status === "Publicado"
                                  ? "bg-[#b9fa01] shadow-[0_0_8px_rgba(185,250,1,0.5)]"
                                  : flow.status === "Pausado"
                                  ? "bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.5)]"
                                  : "bg-white/40"
                              }`}
                            />
                            <span className="text-[12px] font-medium text-neutral-300">
                              {flow.status}
                            </span>
                          </div>
                        </td>
                        <td className="px-4 text-white/50 tabular-nums">
                          {flow.lastRun}
                        </td>
                        <td className="px-4 text-white/50">
                          {flow.createdBy}
                        </td>
                        <td className="w-12 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                          <div className="relative inline-block text-left">
                            <button
                              type="button"
                              onClick={(e) => {
                                e.stopPropagation();
                                setMenuOpenFlowId(menuOpenFlowId === flow.id ? null : flow.id);
                              }}
                              className="size-7 rounded-[6px] hover:bg-white/[0.08] text-white/40 hover:text-white transition-colors flex items-center justify-center cursor-pointer"
                              title="Opciones de flujo"
                              aria-label="Opciones de flujo"
                            >
                              <MoreVertical className="size-4" />
                            </button>

                            {menuOpenFlowId === flow.id && (
                              <div
                                className="absolute right-0 top-8 w-48 bg-[#0c0c10] border border-white/[0.1] rounded-[8px] p-1.5 shadow-2xl z-50 text-[12px] divide-y divide-white/[0.06]"
                                onClick={(e) => e.stopPropagation()}
                              >
                                <div className="space-y-0.5 pb-1">
                                  <button
                                    type="button"
                                    onClick={() => {
                                      setMenuOpenFlowId(null);
                                      setOpenedFlow(flow);
                                    }}
                                    className="w-full text-left px-2.5 py-1.5 rounded-[5px] text-white hover:bg-white/[0.06] flex items-center gap-2 transition-colors cursor-pointer"
                                  >
                                    <Code className="size-3.5 text-[#b9fa01]" />
                                    <span>Abrir en canvas</span>
                                  </button>

                                  <button
                                    type="button"
                                    onClick={() => {
                                      setRenameModalFlow(flow);
                                      setRenameName(flow.name);
                                      setRenameDesc(flow.description);
                                      setMenuOpenFlowId(null);
                                    }}
                                    className="w-full text-left px-2.5 py-1.5 rounded-[5px] text-white hover:bg-white/[0.06] flex items-center gap-2 transition-colors cursor-pointer"
                                  >
                                    <Pencil className="size-3.5 text-white/60" />
                                    <span>Renombrar</span>
                                  </button>

                                  <button
                                    type="button"
                                    onClick={() => handleDuplicateFlow(flow)}
                                    className="w-full text-left px-2.5 py-1.5 rounded-[5px] text-white hover:bg-white/[0.06] flex items-center gap-2 transition-colors cursor-pointer"
                                  >
                                    <Copy className="size-3.5 text-white/60" />
                                    <span>Duplicar</span>
                                  </button>

                                  <button
                                    type="button"
                                    onClick={() => handleExportJSON(flow)}
                                    className="w-full text-left px-2.5 py-1.5 rounded-[5px] text-white hover:bg-white/[0.06] flex items-center gap-2 transition-colors cursor-pointer"
                                  >
                                    <Download className="size-3.5 text-white/60" />
                                    <span>Exportar JSON</span>
                                  </button>

                                  <button
                                    type="button"
                                    onClick={() => handleToggleStatus(flow.id)}
                                    className="w-full text-left px-2.5 py-1.5 rounded-[5px] text-white hover:bg-white/[0.06] flex items-center gap-2 transition-colors cursor-pointer"
                                  >
                                    {flow.status === "Publicado" ? (
                                      <>
                                        <Pause className="size-3.5 text-amber-400" />
                                        <span>Pausar flujo</span>
                                      </>
                                    ) : (
                                      <>
                                        <Play className="size-3.5 text-[#b9fa01]" />
                                        <span>Publicar flujo</span>
                                      </>
                                    )}
                                  </button>
                                </div>

                                <div className="pt-1">
                                  <button
                                    type="button"
                                    onClick={() => {
                                      setDeleteConfirmFlowIds([flow.id]);
                                      setMenuOpenFlowId(null);
                                    }}
                                    className="w-full text-left px-2.5 py-1.5 rounded-[5px] text-rose-400 hover:bg-rose-500/10 flex items-center gap-2 transition-colors cursor-pointer font-medium"
                                  >
                                    <Trash2 className="size-3.5 text-rose-400" />
                                    <span>Eliminar flujo</span>
                                  </button>
                                </div>
                              </div>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 2: CREDENCIALES (PATRÓN C) */}
        {activeTab === "credenciales" && (
          <div className="mt-5 space-y-3">
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-3 flex-1 max-w-md">
                <input
                  type="text"
                  value={searchCred}
                  onChange={(e) => setSearchCred(e.target.value)}
                  placeholder="Buscar credenciales..."
                  className="w-full px-3 py-1.5 rounded-[6px] bg-[#070709] border border-white/[0.08] text-[13px] text-white placeholder-white/30 focus:outline-hidden focus:border-[#b9fa01]"
                />
                <select
                  value={credSort}
                  onChange={(e) => setCredSort(e.target.value as any)}
                  className="px-3 py-1.5 rounded-[6px] bg-[#070709] border border-white/[0.08] text-[13px] text-white/70 focus:outline-hidden cursor-pointer"
                >
                  <option value="name">Ordenar por nombre</option>
                  <option value="recent">Más recientes</option>
                </select>
              </div>

              <button
                type="button"
                className="p-2 rounded-md hover:bg-white/[0.06] text-white/50 hover:text-white transition-colors cursor-pointer shrink-0"
                title="Filtrar credenciales"
                aria-label="Filtrar credenciales"
              >
                <Filter className="size-4" />
              </button>
            </div>

            <div
              className="divide-y divide-white/[0.04] bg-[#070709] rounded-[10px] overflow-hidden"
              style={{ boxShadow: "0 0 0 1px rgba(255,255,255,0.06)" }}
            >
              {filteredCredentials.map((cred) => (
                <div
                  key={cred.id}
                  className="p-4 flex items-center justify-between hover:bg-[#0f0f13] transition-colors"
                >
                  <div className="flex items-center gap-3.5 min-w-0">
                    <ServiceLogo type={cred.serviceType} />
                    <div className="min-w-0">
                      <div className="text-[13px] font-medium text-white truncate">
                        {cred.name}
                      </div>
                      <div className="text-[11px] text-white/40 truncate mt-0.5 font-mono">
                        {cred.service}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    <span className="text-[11px] px-2 py-0.5 rounded border border-white/[0.08] text-white/50 font-mono">
                      {cred.scope}
                    </span>
                    <button
                      type="button"
                      className="p-1 rounded text-white/40 hover:text-white hover:bg-white/[0.06] cursor-pointer transition-colors"
                      title="Opciones de credencial"
                      aria-label="Opciones de credencial"
                    >
                      <MoreVertical className="size-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 3: EJECUCIONES (PATRÓN A) */}
        {activeTab === "ejecuciones" && (
          <div className="mt-5">
            <div className="flex items-center justify-between">
              <label className="inline-flex items-center gap-2 cursor-pointer text-[12px] text-white/50 hover:text-white/70 transition-colors">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="size-3.5 rounded accent-[#b9fa01] cursor-pointer"
                />
                <span>Actualización automática</span>
              </label>

              <button
                type="button"
                className="p-1.5 rounded-md hover:bg-white/[0.06] text-white/50 hover:text-white transition-colors cursor-pointer"
                title="Filtrar ejecuciones"
                aria-label="Filtrar ejecuciones"
              >
                <Filter className="size-4" />
              </button>
            </div>

            <div
              className="mt-3 rounded-[10px] overflow-hidden bg-[#070709]"
              style={{ boxShadow: "0 0 0 1px rgba(255,255,255,0.06)" }}
            >
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-[#0a0a0d] h-10 text-[11px] font-semibold text-white/50 tracking-[0.03em] uppercase border-b border-white/[0.06]">
                    <th className="w-12 px-4">
                      <input
                        type="checkbox"
                        className="size-3.5 rounded accent-[#b9fa01] cursor-pointer"
                        aria-label="Seleccionar todo"
                      />
                    </th>
                    <th className="px-4 font-semibold">ESTADO</th>
                    <th className="px-4 font-semibold">FLUJO</th>
                    <th className="px-4 font-semibold">INICIO</th>
                    <th className="px-4 font-semibold">DURACIÓN</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/[0.04]">
                  {INITIAL_EXECUTIONS.map((exec) => (
                    <tr
                      key={exec.id}
                      className="h-12 text-[13px] hover:bg-[#0f0f13] transition-colors duration-150"
                    >
                      <td className="w-12 px-4">
                        <input
                          type="checkbox"
                          className="size-3.5 rounded accent-[#b9fa01] cursor-pointer"
                        />
                      </td>
                      <td className="px-4">
                        <div className="inline-flex items-center gap-2">
                          <span className="size-1.5 rounded-full bg-emerald-400" />
                          <span className="text-[12px] font-medium text-neutral-300">
                            {exec.status}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 font-medium text-white">
                        {exec.flowName}
                      </td>
                      <td className="px-4 text-white/50 tabular-nums">
                        {exec.startTime}
                      </td>
                      <td className="px-4 text-white/50 font-mono tabular-nums">
                        {exec.duration}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 4: VARIABLES (PATRÓN B) */}
        {activeTab === "variables" && (
          <div className="mt-5">
            <div className="w-full border border-dashed border-white/[0.08] bg-[#040406] rounded-[10px] py-16 px-6 flex flex-col items-center justify-center text-center gap-3">
              <h3 className="text-[15px] font-semibold text-white">
                Variables de entorno y secretos
              </h3>
              <p className="text-[13px] text-white/50 max-w-[480px] leading-[1.6]">
                Define variables globales, credenciales cifradas y parámetros compartidos entre todas tus automatizaciones.
              </p>
              <button
                type="button"
                className="mt-2 px-4 py-2 rounded-[6px] border border-white/[0.12] hover:border-white/20 text-white text-[12px] font-medium hover:bg-white/[0.04] transition-colors cursor-pointer"
              >
                Desbloquear variables globales
              </button>
            </div>
          </div>
        )}

        {/* TAB 5: TABLAS DE DATOS (PATRÓN B) */}
        {activeTab === "tablas" && (
          <div className="mt-5">
            <div className="w-full border border-dashed border-white/[0.08] bg-[#040406] rounded-[10px] py-16 px-6 flex flex-col items-center justify-center text-center gap-3">
              <h3 className="text-[15px] font-semibold text-white">
                Tablas de datos no configuradas
              </h3>
              <p className="text-[13px] text-white/50 max-w-[480px] leading-[1.6]">
                Almacena y sincroniza registros estructurados entre tus widgets de atención y bases de datos internas.
              </p>
              <button
                type="button"
                className="mt-2 px-4 py-2 rounded-[6px] bg-[#b9fa01] hover:bg-[#a5e000] text-black text-[12px] font-semibold transition-colors cursor-pointer"
              >
                Crear tabla
              </button>
            </div>
          </div>
        )}

        {/* ── BACKDROP PARA CERRAR MENÚ CONTEXTUAL AL HACER CLIC FUERA ────── */}
        {menuOpenFlowId && (
          <div
            className="fixed inset-0 z-40 bg-transparent"
            onClick={() => setMenuOpenFlowId(null)}
          />
        )}

        {/* ── BARRA FLOTANTE DE ACCIONES EN LOTE (BULK ACTIONS BAR) ────────── */}
        {selectedFlowIds.length > 0 && (
          <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50">
            <div className="flex items-center gap-2 p-2 px-3.5 rounded-[10px] bg-[#121216] border border-white/[0.14] shadow-[0_16px_40px_rgba(0,0,0,0.85)] backdrop-blur-md">
              <span className="px-2.5 py-1 rounded bg-[#b9fa01]/15 text-[#b9fa01] font-mono text-[11px] font-semibold tracking-tight">
                {selectedFlowIds.length} seleccionado{selectedFlowIds.length > 1 ? "s" : ""}
              </span>

              <div className="h-4 w-px bg-white/15 mx-1" />

              <button
                type="button"
                onClick={handleBulkPublish}
                className="px-2.5 py-1 rounded-[6px] hover:bg-white/[0.08] text-[12px] font-medium text-white flex items-center gap-1.5 transition-colors cursor-pointer"
                title="Publicar flujos seleccionados"
              >
                <Play className="size-3 text-[#b9fa01] fill-[#b9fa01]" />
                <span>Publicar</span>
              </button>

              <button
                type="button"
                onClick={handleBulkPause}
                className="px-2.5 py-1 rounded-[6px] hover:bg-white/[0.08] text-[12px] font-medium text-white/80 hover:text-white flex items-center gap-1.5 transition-colors cursor-pointer"
                title="Pausar flujos seleccionados"
              >
                <Pause className="size-3 text-amber-400 fill-amber-400" />
                <span>Pausar</span>
              </button>

              <button
                type="button"
                onClick={handleBulkDuplicate}
                className="px-2.5 py-1 rounded-[6px] hover:bg-white/[0.08] text-[12px] font-medium text-white/80 hover:text-white flex items-center gap-1.5 transition-colors cursor-pointer"
                title="Duplicar flujos seleccionados"
              >
                <Copy className="size-3 text-white/70" />
                <span>Duplicar</span>
              </button>

              <button
                type="button"
                onClick={handleBulkExportJSON}
                className="px-2.5 py-1 rounded-[6px] hover:bg-white/[0.08] text-[12px] font-medium text-white/80 hover:text-white flex items-center gap-1.5 transition-colors cursor-pointer"
                title="Exportar flujos a JSON"
              >
                <Download className="size-3 text-white/70" />
                <span>Exportar</span>
              </button>

              <div className="h-4 w-px bg-white/15 mx-1" />

              <button
                type="button"
                onClick={handleBulkDelete}
                className="px-2.5 py-1 rounded-[6px] hover:bg-rose-500/15 text-[12px] font-medium text-rose-400 hover:text-rose-300 flex items-center gap-1.5 transition-colors cursor-pointer"
                title="Eliminar flujos seleccionados"
              >
                <Trash2 className="size-3 text-rose-400" />
                <span>Eliminar</span>
              </button>

              <button
                type="button"
                onClick={() => setSelectedFlowIds([])}
                className="p-1 rounded-[5px] hover:bg-white/[0.08] text-white/40 hover:text-white transition-colors cursor-pointer ml-1"
                title="Deseleccionar todos"
              >
                <X className="size-3.5" />
              </button>
            </div>
          </div>
        )}

        {/* ── MODAL: RENOMBRAR FLUJO ───────────────────────────────────────── */}
        {renameModalFlow && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-xs p-4">
            <div className="w-full max-w-md bg-[#0c0c10] border border-white/[0.1] rounded-[10px] p-6 shadow-2xl space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-white/[0.06]">
                <h3 className="text-[15px] font-semibold text-white">Renombrar flujo</h3>
                <button
                  type="button"
                  onClick={() => setRenameModalFlow(null)}
                  className="p-1 rounded text-white/40 hover:text-white transition-colors cursor-pointer"
                >
                  <X className="size-4" />
                </button>
              </div>

              <div className="space-y-3">
                <div>
                  <label className="block text-[11px] font-semibold text-white/50 uppercase tracking-wider mb-1.5">
                    Nombre del flujo
                  </label>
                  <input
                    type="text"
                    value={renameName}
                    onChange={(e) => setRenameName(e.target.value)}
                    className="w-full px-3 py-2 rounded-[6px] bg-[#070709] border border-white/[0.1] text-[13px] text-white focus:outline-hidden focus:border-[#b9fa01]"
                    autoFocus
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-semibold text-white/50 uppercase tracking-wider mb-1.5">
                    Descripción
                  </label>
                  <input
                    type="text"
                    value={renameDesc}
                    onChange={(e) => setRenameDesc(e.target.value)}
                    className="w-full px-3 py-2 rounded-[6px] bg-[#070709] border border-white/[0.1] text-[13px] text-white focus:outline-hidden focus:border-[#b9fa01]"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-white/[0.06]">
                <button
                  type="button"
                  onClick={() => setRenameModalFlow(null)}
                  className="px-3.5 py-1.5 rounded-[6px] border border-white/[0.1] text-[12px] font-medium text-white/70 hover:text-white hover:bg-white/[0.04] transition-colors cursor-pointer"
                >
                  Cancelar
                </button>
                <button
                  type="button"
                  onClick={() => {
                    if (renameName.trim()) {
                      setFlows((prev) =>
                        prev.map((f) =>
                          f.id === renameModalFlow.id
                            ? { ...f, name: renameName.trim(), description: renameDesc.trim() }
                            : f
                        )
                      );
                      setRenameModalFlow(null);
                    }
                  }}
                  className="px-4 py-1.5 rounded-[6px] bg-[#b9fa01] hover:bg-[#a5e000] text-[12px] font-semibold text-black transition-colors cursor-pointer"
                >
                  Guardar cambios
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ── MODAL: CONFIRMAR ELIMINACIÓN ─────────────────────────────────── */}
        {deleteConfirmFlowIds && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-xs p-4">
            <div className="w-full max-w-md bg-[#0c0c10] border border-rose-500/25 rounded-[10px] p-6 shadow-2xl space-y-4">
              <div className="flex items-center gap-3 text-rose-400">
                <div className="size-9 rounded-full bg-rose-500/10 flex items-center justify-center shrink-0">
                  <Trash2 className="size-5" />
                </div>
                <h3 className="text-[15px] font-semibold text-white">
                  {deleteConfirmFlowIds.length > 1
                    ? `¿Eliminar ${deleteConfirmFlowIds.length} flujos?`
                    : "¿Eliminar flujo de automatización?"}
                </h3>
              </div>

              <p className="text-[13px] text-white/60 leading-relaxed">
                Esta acción no se puede deshacer. Los disparadores y automatizaciones de{" "}
                {deleteConfirmFlowIds.length > 1 ? "estos flujos" : "este flujo"} dejarán de operar de inmediato.
              </p>

              <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-white/[0.06]">
                <button
                  type="button"
                  onClick={() => setDeleteConfirmFlowIds(null)}
                  className="px-3.5 py-1.5 rounded-[6px] border border-white/[0.1] text-[12px] font-medium text-white/70 hover:text-white hover:bg-white/[0.04] transition-colors cursor-pointer"
                >
                  Cancelar
                </button>
                <button
                  type="button"
                  onClick={handleConfirmDelete}
                  className="px-4 py-1.5 rounded-[6px] bg-rose-600 hover:bg-rose-500 text-[12px] font-semibold text-white transition-colors cursor-pointer"
                >
                  Eliminar definitivamente
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </AppShell>
  );
}
