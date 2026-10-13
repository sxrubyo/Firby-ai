"use client";

import { useState, useEffect } from "react";
import { AppShell } from "@/components/app-shell";
import { BarChart3, MessageSquare, Server, Clock, RefreshCw, AlertCircle } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

export default function AnalyticsPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDark, setIsDark] = useState(true);

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem("dev_master_key") || "";
      const res = await fetch("/api/dev/analytics", {
        headers: { "x-master-key": token }
      });
      if (!res.ok) throw new Error("Could not load analytics");
      const json = await res.json();
      setData(json);
    } catch (e: any) {
      console.error(e);
      setError(e.message || "Failed to load analytics");
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  return (
    <AppShell fullWidth={true}>
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-neutral-900 dark:text-white">Métricas y Rendimiento</h1>
            <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1">Métricas globales y estadísticas de operación.</p>
          </div>
          <button onClick={fetchAnalytics} className="p-2 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-md hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors cursor-pointer">
            <RefreshCw className={`w-5 h-5 text-neutral-600 dark:text-neutral-300 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>

          {error && (
            <div className="flex items-center gap-2 p-4 bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 rounded-xl">
                <AlertCircle className="w-5 h-5" />
                <span className="font-medium">{error}</span>
            </div>
          )}

          {loading && !data ? (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 animate-pulse">
                  {[1,2,3,4].map(i => <div key={i} className="h-32 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl"></div>)}
              </div>
          ) : data ? (
              <>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div className="p-6 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl shadow-sm">
                          <div className="flex items-center justify-between mb-4">
                              <span className="text-sm font-medium text-neutral-500">Total Messages</span>
                              <MessageSquare className="w-4 h-4 text-neutral-400" />
                          </div>
                          <span className="text-3xl font-bold">{data.total_messages?.toLocaleString() || 0}</span>
                      </div>
                      <div className="p-6 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl shadow-sm">
                          <div className="flex items-center justify-between mb-4">
                              <span className="text-sm font-medium text-neutral-500">Messages Today</span>
                              <BarChart3 className="w-4 h-4 text-neutral-400" />
                          </div>
                          <span className="text-3xl font-bold">{data.messages_today?.toLocaleString() || 0}</span>
                      </div>
                      <div className="p-6 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl shadow-sm">
                          <div className="flex items-center justify-between mb-4">
                              <span className="text-sm font-medium text-neutral-500">Active DBs Scanned</span>
                              <Server className="w-4 h-4 text-neutral-400" />
                          </div>
                          <span className="text-3xl font-bold">{data.messages_per_instance?.length || 0}</span>
                      </div>
                      <div className="p-6 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl shadow-sm">
                          <div className="flex items-center justify-between mb-4">
                              <span className="text-sm font-medium text-neutral-500">Avg Response Time</span>
                              <Clock className="w-4 h-4 text-neutral-400" />
                          </div>
                          <span className="text-3xl font-bold">1.2s</span>
                      </div>
                  </div>

                  <div className="p-6 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl shadow-sm h-[400px] flex flex-col">
                      <h2 className="text-lg font-semibold mb-6">Messages per Instance</h2>
                      {data.messages_per_instance?.length > 0 ? (
                          <div className="flex-1 w-full min-w-0">
                              <ResponsiveContainer width="100%" height="100%">
                                  <BarChart data={data.messages_per_instance} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#333" opacity={0.2} />
                                      <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#888' }} />
                                      <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#888' }} />
                                      <Tooltip 
                                          cursor={{ fill: 'transparent' }}
                                          contentStyle={{ backgroundColor: '#111', border: '1px solid #333', borderRadius: '8px', color: '#fff' }}
                                          itemStyle={{ color: '#e05a2b' }}
                                      />
                                      <Bar dataKey="messages" radius={[4, 4, 0, 0]} maxBarSize={60}>
                                        {data.messages_per_instance.map((entry: any, index: number) => (
                                          <Cell key={`cell-${index}`} fill={index === 0 ? '#e05a2b' : '#333333'} />
                                        ))}
                                      </Bar>
                                  </BarChart>
                              </ResponsiveContainer>
                          </div>
                      ) : (
                          <div className="flex-1 flex items-center justify-center text-neutral-500">
                              No instance data available.
                          </div>
                      )}
                  </div>
              </>
          ) : null}
        </div>
      </AppShell>
    );
  }
