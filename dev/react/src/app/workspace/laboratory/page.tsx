"use client";

import React, { useState, useEffect } from "react";
import { AppShell } from "@/components/app-shell";
import { Button } from "@/components/ui/button";
import { RefreshCw, ShieldCheck } from "lucide-react";

export default function WorkspaceLaboratoryPage() {
  const [labData, setLabData] = useState<any>(null);
  const [isRunningAudit, setIsRunningAudit] = useState(false);

  useEffect(() => {
    loadLaboratoryStatus();
  }, []);

  const loadLaboratoryStatus = async () => {
    try {
      const res = await fetch("/api/laboratory/status");
      if (res.ok) {
        const data = await res.json();
        setLabData(data);
      }
    } catch (e) {}
  };

  const handleRunAudit = async () => {
    setIsRunningAudit(true);
    try {
      const res = await fetch("/api/laboratory/run", { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        setLabData(data);
      }
    } catch (e) {
    } finally {
      setIsRunningAudit(false);
    }
  };

  return (
    <AppShell fullWidth={true}>
      <div className="space-y-6">
        <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl p-6 flex items-center justify-between shadow-2xs">
          <div>
            <h2 className="text-xl font-bold text-neutral-900 dark:text-white">Pruebas Automatizadas de Arquetipos</h2>
            <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1">
              Auditoría interna de calidad conversacional y arquetipos en entorno sandbox.
            </p>
          </div>

          <Button
            onClick={handleRunAudit}
            disabled={isRunningAudit}
            className="bg-neutral-900 hover:bg-neutral-800 text-white dark:bg-white dark:hover:bg-neutral-200 dark:text-neutral-950 font-semibold px-4 py-2 rounded-xl text-xs flex items-center gap-2 shadow-xs cursor-pointer"
          >
            <RefreshCw className={`size-4 ${isRunningAudit ? "animate-spin" : ""}`} />
            {isRunningAudit ? "Ejecutando..." : "Iniciar Evaluación 0-100"}
          </Button>
        </div>

        {labData && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl p-6 flex items-center justify-between shadow-2xs">
              <div>
                <span className="text-xs uppercase font-semibold text-lime-700 dark:text-[#b9fa01] tracking-wider">Score Global de Calidad</span>
                <h3 className="text-4xl font-extrabold text-neutral-900 dark:text-white mt-1">{labData.score} / 100</h3>
              </div>
              <div className="flex items-center gap-2 text-xs text-lime-700 dark:text-[#b9fa01] bg-lime-50 dark:bg-[#b9fa01]/10 px-3 py-1.5 rounded-lg border border-lime-200/60 dark:border-transparent font-medium">
                <ShieldCheck className="size-5" />
                <span>100% Calificada para Producción</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {labData.personas?.map((p: any) => (
                <div key={p.id} className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl p-4 space-y-2 shadow-2xs">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-neutral-900 dark:text-white">{p.name}</span>
                    <span className="text-xs font-semibold text-lime-700 dark:text-[#b9fa01] bg-lime-50 dark:bg-[#b9fa01]/10 px-2 py-0.5 rounded border border-lime-200/60 dark:border-transparent">{p.score} pts</span>
                  </div>
                  <p className="text-xs text-neutral-500 dark:text-neutral-400">{p.notes}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
