"use client";

import React, { useState, useEffect } from "react";
import { AppShell } from "@/components/app-shell";

export default function WorkspaceKanbanPage() {
  const [kanbanLeads, setKanbanLeads] = useState<any[]>([]);

  useEffect(() => {
    loadKanbanLeads();
  }, []);

  const loadKanbanLeads = async () => {
    try {
      const res = await fetch("/api/kanban/leads");
      if (res.ok) {
        const data = await res.json();
        setKanbanLeads(data.leads || []);
      }
    } catch (e) {}
  };

  return (
    <AppShell fullWidth={true}>
      <div className="space-y-6">
        <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl p-6 shadow-2xs">
          <h2 className="text-xl font-bold text-neutral-900 dark:text-white">Pipeline de Citas y Clientes</h2>
          <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1">
            Seguimiento de prospectos y conversaciones clasificadas automáticamente por Firby.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl p-4 space-y-3 shadow-2xs">
            <span className="text-xs font-semibold text-neutral-700 dark:text-neutral-300 uppercase tracking-wider">En Conversación</span>
            {kanbanLeads.filter(l => l.stage === "en_conversacion" || l.stage === "nuevo").map(lead => (
              <div key={lead.id} className="bg-neutral-50 dark:bg-neutral-800/60 border border-neutral-200 dark:border-neutral-700 p-3 rounded-lg space-y-1">
                <div className="text-xs font-semibold text-neutral-900 dark:text-white">{lead.name}</div>
                <span className="text-[10px] text-lime-700 dark:text-[#b9fa01] bg-lime-50 dark:bg-[#b9fa01]/10 px-1.5 py-0.5 rounded font-medium border border-lime-200/60 dark:border-transparent">{lead.ai_intent}</span>
                <div className="text-[11px] text-neutral-500 dark:text-neutral-400 truncate">"{lead.last_msg}"</div>
              </div>
            ))}
          </div>

          <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl p-4 space-y-3 shadow-2xs">
            <span className="text-xs font-semibold text-amber-600 dark:text-amber-400 uppercase tracking-wider">Interesados</span>
            {kanbanLeads.filter(l => l.stage === "interesado").map(lead => (
              <div key={lead.id} className="bg-neutral-50 dark:bg-neutral-800/60 border border-amber-200 dark:border-amber-500/30 p-3 rounded-lg space-y-1">
                <div className="text-xs font-semibold text-neutral-900 dark:text-white">{lead.name}</div>
                <span className="text-[10px] text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-500/10 px-1.5 py-0.5 rounded font-medium border border-amber-200/60 dark:border-transparent">{lead.ai_intent}</span>
                <div className="text-[11px] text-neutral-500 dark:text-neutral-400 truncate">"{lead.last_msg}"</div>
              </div>
            ))}
          </div>

          <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl p-4 space-y-3 shadow-2xs">
            <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">Citas Agendadas</span>
            {kanbanLeads.filter(l => l.stage === "agendado").map(lead => (
              <div key={lead.id} className="bg-neutral-50 dark:bg-neutral-800/60 border border-emerald-200 dark:border-emerald-500/30 p-3 rounded-lg space-y-1">
                <div className="text-xs font-semibold text-neutral-900 dark:text-white">{lead.name}</div>
                <span className="text-[10px] text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-500/10 px-1.5 py-0.5 rounded font-medium border border-emerald-200/60 dark:border-transparent">{lead.ai_intent}</span>
                <div className="text-[11px] text-neutral-500 dark:text-neutral-400 truncate">"{lead.last_msg}"</div>
              </div>
            ))}
          </div>

          <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl p-4 space-y-3 shadow-2xs">
            <span className="text-xs font-semibold text-neutral-700 dark:text-neutral-300 uppercase tracking-wider">Clientes Confirmados</span>
            <div className="text-center py-6 text-xs text-neutral-400 italic">No hay clientes aún</div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
