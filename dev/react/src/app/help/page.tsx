"use client";
import { AppShell } from "@/components/app-shell";
import { Wrench } from "lucide-react";

export default function ComingSoonPage() {
  return (
    <AppShell>
      <div className="flex flex-col items-center justify-center max-w-md mx-auto py-16 text-center">
        <div className="w-20 h-20 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 shadow-sm rounded-full flex items-center justify-center mb-6">
          <Wrench className="w-8 h-8 text-neutral-500 dark:text-neutral-400" strokeWidth={1.5} />
        </div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white mb-2">Centro de Ayuda</h1>
        <p className="text-xs text-neutral-500 dark:text-neutral-400 leading-relaxed mb-6">
          Estamos preparando guías interactivas y documentación de integración rápida para tu operador de IA.
        </p>
        <a
          href="mailto:soporte@firbyai.com"
          className="inline-flex items-center justify-center px-4 py-2 rounded-lg bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 text-xs font-semibold hover:opacity-90 transition-opacity"
        >
          Contactar soporte
        </a>
      </div>
    </AppShell>
  );
}
