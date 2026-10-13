"use client";

import { useState, useEffect } from "react";
import { AppShell } from "@/components/app-shell";
import { Plus, Trash2, RefreshCw, Server, Activity, Settings2, Play, Square, AlertCircle, X, Save } from "lucide-react";

export default function InstancesPage() {
  const [instances, setInstances] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const [configuringInstance, setConfiguringInstance] = useState<any | null>(null);
  const [instancePrompt, setInstancePrompt] = useState("");
  const [savingPrompt, setSavingPrompt] = useState(false);
  const [isDark, setIsDark] = useState(true);

  const [error, setError] = useState<string | null>(null);

  const fetchInstances = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem("dev_master_key") || "";
      const res = await fetch("/api/dev/instances", {
        headers: {
            "x-master-key": token
        }
      });
      if (!res.ok) {
          throw new Error("Could not load instances");
      }
      const data = await res.json();
      setInstances(data.instances || []);
    } catch (e: any) {
      console.error(e);
      setError(e.message || "Failed to load instances");
    }
    setLoading(false);
  };

  
  const openConfigure = async (inst: any) => {
      setConfiguringInstance(inst);
      setInstancePrompt("Loading prompt...");
      try {
          const token = localStorage.getItem("dev_master_key") || "";
          const res = await fetch(`/api/dev/instances/${inst.name}/prompt`, {
              headers: { "x-master-key": token }
          });
          if (res.ok) {
              const data = await res.json();
              setInstancePrompt(data.prompt || "");
          } else {
              setInstancePrompt("Error loading prompt.");
          }
      } catch (e) {
          setInstancePrompt("Error loading prompt.");
      }
  };

  const saveConfigure = async () => {
      if(!configuringInstance) return;
      setSavingPrompt(true);
      try {
          const token = localStorage.getItem("dev_master_key") || "";
          const res = await fetch(`/api/dev/instances/${configuringInstance.name}/prompt`, {
              method: "POST",
              headers: { 
                  "Content-Type": "application/json",
                  "x-master-key": token 
              },
              body: JSON.stringify({ prompt: instancePrompt })
          });
          if (res.ok) {
              setConfiguringInstance(null);
          } else {
              alert("Error saving prompt.");
          }
      } catch (e) {
          alert("Error saving prompt.");
      }
      setSavingPrompt(false);
  };

  useEffect(() => {
    fetchInstances();
  }, []);

  const createInstance = async () => {
    try {
      const token = localStorage.getItem("dev_master_key") || "";
      const res = await fetch("/api/dev/instances/new", {
        method: "POST",
        headers: { 
            "Content-Type": "application/json",
            "x-master-key": token
        },
        body: JSON.stringify({ name: "nueva-instancia" })
      });
      if (res.ok) fetchInstances();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <AppShell fullWidth={true}>
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Equipo e Instancias</h1>
            <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1">Gestión de miembros y sedes operativas de Firby.</p>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={fetchInstances} className="p-2 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-md hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors cursor-pointer">
              <RefreshCw className={`w-5 h-5 text-neutral-600 dark:text-neutral-300 ${loading ? "animate-spin" : ""}`} />
            </button>
            <button onClick={createInstance} className="flex items-center gap-2 px-4 py-2 bg-neutral-900 hover:bg-neutral-800 text-white dark:bg-white dark:hover:bg-neutral-200 dark:text-neutral-950 font-semibold text-xs rounded-xl shadow-xs transition-colors cursor-pointer">
              <Plus className="w-4 h-4" /> Nueva Sede / Instancia
            </button>
          </div>
        </div>

          {error && (
            <div className="flex items-center justify-between p-4 bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 rounded-xl">
                <div className="flex items-center gap-2">
                    <AlertCircle className="w-5 h-5" />
                    <span className="font-medium">{error}</span>
                </div>
                <button onClick={fetchInstances} className="px-3 py-1 text-sm font-medium bg-red-500/20 hover:bg-red-500/30 rounded-md transition-colors">
                    Retry
                </button>
            </div>
          )}

          <div className="grid gap-4">
            {loading && instances.length === 0 ? (
                // Skeletons
                <>
                    {[1, 2, 3].map(i => (
                        <div key={i} className="flex items-center justify-between p-5 bg-white dark:bg-neutral-900/50 border border-neutral-200 dark:border-neutral-800 rounded-xl animate-pulse">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 bg-neutral-200 dark:bg-neutral-800 rounded-lg"></div>
                                <div className="space-y-2">
                                    <div className="h-5 w-32 bg-neutral-200 dark:bg-neutral-800 rounded"></div>
                                    <div className="h-4 w-48 bg-neutral-200 dark:bg-neutral-800 rounded"></div>
                                </div>
                            </div>
                        </div>
                    ))}
                </>
            ) : (
                instances.map(inst => (
                  <div key={inst.name} className="flex items-center justify-between p-5 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl hover:border-neutral-300 dark:hover:border-neutral-700 transition-colors shadow-sm">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-neutral-100 dark:bg-neutral-950 rounded-lg border border-neutral-200 dark:border-neutral-800 flex items-center justify-center">
                        <Server className="w-6 h-6 text-neutral-500 dark:text-neutral-400" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-lg text-neutral-900 dark:text-white">{inst.name}</h3>
                        <div className="flex items-center gap-3 text-sm text-neutral-500 dark:text-neutral-400 mt-1">
                          <span className="flex items-center gap-1 font-medium capitalize">
                            <span className={`w-2 h-2 rounded-full ${inst.status === 'online' ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
                            <span className={inst.status === 'online' ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'}>
                                {inst.status}
                            </span>
                          </span>
                          <span>•</span>
                          <span>{inst.sector || 'N/A'}</span>
                          <span>•</span>
                          <span>Port: {inst.port}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-3">
                      {inst.status === 'online' ? (
                          <button className="flex items-center justify-center w-10 h-10 border border-neutral-200 dark:border-neutral-800 text-neutral-600 dark:text-neutral-300 hover:bg-red-500/10 hover:text-red-500 hover:border-red-500/20 rounded-md transition-colors" title="Stop">
                            <Square className="w-4 h-4 fill-current" />
                          </button>
                      ) : (
                          <button className="flex items-center justify-center w-10 h-10 border border-neutral-200 dark:border-neutral-800 text-neutral-600 dark:text-neutral-300 hover:bg-emerald-500/10 hover:text-emerald-500 hover:border-emerald-500/20 rounded-md transition-colors" title="Start">
                            <Play className="w-4 h-4 fill-current" />
                          </button>
                      )}
                      
                      <button className="flex items-center justify-center w-10 h-10 border border-neutral-200 dark:border-neutral-800 text-neutral-600 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-md transition-colors" title="Configure">
                        <Settings2 className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                ))
            )}
            {!loading && instances.length === 0 && !error && (
              <div className="text-center py-12 text-neutral-500 border border-dashed border-neutral-200 dark:border-neutral-800 rounded-xl">
                No instances found.
              </div>
            )}
          </div>
        </div>
      
      {configuringInstance && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl shadow-2xl w-full max-w-3xl flex flex-col max-h-[90vh]">
                <div className="flex items-center justify-between p-5 border-b border-neutral-200 dark:border-neutral-800">
                    <div>
                        <h2 className="text-xl font-bold text-neutral-900 dark:text-white">Configure: {configuringInstance.name}</h2>
                        <p className="text-sm text-neutral-500 mt-1">Update system prompt and configuration.</p>
                    </div>
                    <button onClick={() => setConfiguringInstance(null)} className="p-2 text-neutral-500 hover:text-neutral-900 dark:hover:text-white transition-colors">
                        <X className="w-5 h-5" />
                    </button>
                </div>
                <div className="p-5 flex-1 overflow-y-auto">
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">System Prompt</label>
                            <textarea 
                                value={instancePrompt}
                                onChange={(e) => setInstancePrompt(e.target.value)}
                                className="w-full h-96 p-4 bg-neutral-50 dark:bg-black border border-neutral-200 dark:border-neutral-800 rounded-lg text-sm text-neutral-900 dark:text-neutral-200 font-mono resize-none focus:outline-none focus:ring-2 focus:ring-[#e05a2b]"
                                placeholder="Loading..."
                            />
                        </div>
                    </div>
                </div>
                <div className="p-5 border-t border-neutral-200 dark:border-neutral-800 flex justify-end gap-3">
                    <button onClick={() => setConfiguringInstance(null)} className="px-4 py-2 font-medium text-neutral-600 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-md transition-colors">
                        Cancel
                    </button>
                    <button onClick={saveConfigure} disabled={savingPrompt} className="flex items-center gap-2 px-4 py-2 font-medium bg-[#e05a2b] text-white rounded-md hover:bg-[#c94e24] transition-colors disabled:opacity-50">
                        {savingPrompt ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                        Save Prompt
                    </button>
                </div>
            </div>
        </div>
      )}
    </AppShell>
  );
}
