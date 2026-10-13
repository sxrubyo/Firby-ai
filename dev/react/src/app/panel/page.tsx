"use client";
import { ThemeContext } from "@/components/theme-provider";
import { useContext } from "react";

import Link from "next/link";
import React, { useState, useEffect } from "react";
import { AppShell } from "@/components/app-shell";
import { Topbar } from "@/components/ui/topbar";
import { SearchInputLoader } from "@/components/ui/search-input-loader";
import { Caveat } from "next/font/google";

const caveat = Caveat({ subsets: ["latin"] });
import { Bell, Search, ArrowLeft, Calendar, ArrowUpRight, ArrowDownRight, Sun, Moon, ChevronLeft } from "lucide-react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import TableWithDialog from "@/components/ui/table-with-dialog";
import { ClientTokenManager } from "@/components/ui/client-token-manager";



const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-[#1e1e1e] border border-[#333] p-3 rounded-lg text-xs shadow-lg z-50 relative">
        <p className="text-white mb-2 font-medium">{`${label} 1, 2024`}</p>
        <p className="text-red-700 dark:text-red-500">{`Total sales ${payload[0].value}`}</p>
        <p className="text-[#ca8a04]">{`Target sales ${payload[1].value}`}</p>
      </div>
    );
  }
  return null;
};

const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const hours = ['9am', '10am', '11am', '12pm', '1pm', '2pm', '3pm'];



export default function PanelPage() {
  const [greeting, setGreeting] = useState<string>("Dashboard");
  const [currentDate, setCurrentDate] = useState("");
  const [sales, setSales] = useState<any[]>([]);
  const [chartData, setChartData] = useState<any[]>([]);
  const [heatmapData, setHeatmapData] = useState<number[][]>([]);
  const { isDark, toggleDark } = useContext(ThemeContext);
  

  const [dashboardData, setDashboardData] = useState<any>(null);
  
  
  
  useEffect(() => {
    const fetchAllData = async () => {
        try {
            const token = localStorage.getItem("dev_master_key") || "";
            
            // Sales
            fetch("/api/dev/sales", { headers: { "x-master-key": token } })
                .then(res => res.json())
                .then(data => { if(data.sales) setSales(data.sales); })
                .catch(e => console.error(e));

            // Chart
            fetch("/api/dev/chart", { headers: { "x-master-key": token } })
                .then(res => res.json())
                .then(data => { if(data.chartData) setChartData(data.chartData); })
                .catch(e => console.error(e));

            // Heatmap
            fetch("/api/dev/heatmap", { headers: { "x-master-key": token } })
                .then(res => res.json())
                .then(data => { if(data.heatmapData) setHeatmapData(data.heatmapData); })
                .catch(e => console.error(e));

        } catch(e) {}
    };
    fetchAllData();
  }, []);

  useEffect(() => {
    // intelligent date based on locale
    const date = new Date();
    const options: Intl.DateTimeFormatOptions = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
    setCurrentDate(date.toLocaleDateString(undefined, options));
  }, []);

  
  

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const token = localStorage.getItem("dev_master_key") || "";
        const res = await fetch("/api/dev/dashboard", {
            headers: { "x-master-key": token }
        });
        if (res.ok) {
            const data = await res.json();
            setDashboardData(data.metrics);
        }
      } catch (e) {
        console.error(e);
      }
    };
    fetchDashboard();
  }, []);

  const isCollapsed = false;


  
  
  

  
  

  

  
  
  

  
  

  
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem("dev_master_key") || localStorage.getItem("firby_master_key") || localStorage.getItem("conny_master_key") || "";
        const res = await fetch("/api/user/profile", { headers: { "x-master-key": token } });
        let userName = "Usuario";
        if (res.ok) {
          const data = await res.json();
          if (data.name) userName = data.name;
        }

        const hour = new Date().getHours();
        const morningGreetings = [`¡Buenos días, ${userName}!`, `Hola, ${userName}`, `Buen día, ${userName}`, `Excelente mañana, ${userName}`, `¿Qué tal, ${userName}?`, `Feliz mañana, ${userName}`, `Welcome, ${userName}`, `¡Hola de nuevo, ${userName}!`, `Saludos, ${userName}`, `Muy buenos días, ${userName}`];
        const afternoonGreetings = [`¡Buenas tardes, ${userName}!`, `Hola, ${userName}`, `Buena tarde, ${userName}`, `Excelente tarde, ${userName}`, `¿Qué tal, ${userName}?`, `Feliz tarde, ${userName}`, `Welcome, ${userName}`, `¡Hola de nuevo, ${userName}!`, `Saludos, ${userName}`, `Muy buenas tardes, ${userName}`];
        const eveningGreetings = [`¡Buenas noches, ${userName}!`, `Hola, ${userName}`, `Buena noche, ${userName}`, `Excelente noche, ${userName}`, `¿Qué tal, ${userName}?`, `Feliz noche, ${userName}`, `Welcome, ${userName}`, `¡Hola de nuevo, ${userName}!`, `Saludos, ${userName}`, `Muy buenas noches, ${userName}`];
        const generalGreetings = [`Hola, ${userName}`, `Welcome back`, `Welcome, ${userName}`, `Hola de nuevo`, `¡Qué tal, ${userName}!`];
        
        let possibleGreetings = [];
        if (hour >= 5 && hour < 12) {
          possibleGreetings = [...morningGreetings, ...generalGreetings];
        } else if (hour >= 12 && hour < 19) {
          possibleGreetings = [...afternoonGreetings, ...generalGreetings];
        } else {
          possibleGreetings = [...eveningGreetings, ...generalGreetings];
        }
        setGreeting(possibleGreetings[Math.floor(Math.random() * possibleGreetings.length)]);
      } catch (e) {
         setGreeting("Dashboard");
      }
    };
    fetchProfile();
  }, []);


  
  const getKpiDateRange = () => {
    const today = new Date();
    const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
    const options: Intl.DateTimeFormatOptions = { month: 'short', day: '2-digit', year: 'numeric' };
    return `From ${firstDay.toLocaleDateString(undefined, options)} To ${today.toLocaleDateString(undefined, options)}`;
  };

  const getHeatmapColor = (dIndex: number, hIndex: number) => {
    if (heatmapData.length === 0) return 'bg-[#2e2e2e] dark:bg-[#2e2e2e] bg-neutral-200';
    const val = heatmapData[dIndex] ? heatmapData[dIndex][hIndex] : 0;
    if (val > 2000) return 'bg-[#b91c1c] relative overflow-hidden after:content-[""] after:absolute after:inset-0 after:opacity-30 after:bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,0.2)_25%,rgba(255,255,255,0.2)_50%,transparent_50%,transparent_75%,rgba(255,255,255,0.2)_75%,rgba(255,255,255,0.2)_100%)] after:bg-[length:8px_8px]';
    if (val > 1000) return 'bg-[#c24a1a]';
    if (val > 500) return 'bg-[#7a2e10]';
    return 'bg-[#2e2e2e] dark:bg-[#2e2e2e] bg-neutral-200';
  };

  return (
    <AppShell fullWidth={true}>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-2">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-neutral-900 dark:text-white tracking-tight leading-tight">{greeting}</h1>
            <p className="text-sm text-neutral-500 dark:text-neutral-400 font-medium">Resumen general de rendimiento</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-64">
              <SearchInputLoader />
            </div>
            <div className="hidden lg:flex items-center gap-2 text-sm text-neutral-500 dark:text-[#888888]">
              <Calendar className="h-4 w-4" />
              <span>{currentDate}</span>
            </div>
          </div>
        </div>
            
            {/* KPI Cards */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(0, 1fr))", gap: 12 }} className="mb-4">
            {(dashboardData || [
              { label: "Total Conversations", value: "-", growth: "0%", up: true },
              { label: "Messages Sent", value: "-", growth: "0%", up: true },
              { label: "Active Instances", value: "-", growth: "0%", up: true },
              { label: "Avg Response Time", value: "-", growth: "0%", up: true },
            ]).map((kpi: any, i: number) => (
              <div key={i} className="bg-white dark:bg-[#252525] border border-neutral-200 dark:border-[#333] rounded-xl p-4 shadow-sm relative group hover:border-[#991b1b]/50 transition-premium hover:shadow-[0_4px_20px_-4px_rgba(0,0,0,0.1)] dark:hover:shadow-[0_4px_20px_-4px_rgba(0,0,0,0.5)]">
                <div className="text-neutral-500 dark:text-[#888888] text-sm mb-2">{kpi.label}</div>
                <div className="text-lg font-bold text-neutral-900 dark:text-white">{kpi.value || kpi.val}</div>
                <div className="text-neutral-400 dark:text-[#666666] text-[11px] mt-2">{getKpiDateRange()}</div>
                
                <div className={`absolute top-4 right-5 flex items-center gap-1 text-xs font-medium ${kpi.up ? 'text-emerald-500 dark:text-[#4ade80]' : 'text-red-500 dark:text-[#f87171]'}`}>
                  {kpi.up ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
                  {kpi.growth}
                </div>
              </div>
            ))}
          </div>

          {/* Middle Row: Heatmap & AreaChart */}
          <div style={{ display: "grid", gridTemplateColumns: "auto minmax(0, 1fr)", gap: 12 }} className="mb-4">
            
            {/* Heatmap */}
            <div className="bg-white dark:bg-[#252525] border border-neutral-200 dark:border-[#333] rounded-xl p-4 shadow-sm overflow-x-auto">
              <div className="flex items-center justify-between mb-4 min-w-[300px]">
                <h3 className="text-neutral-900 dark:text-white font-medium">Orders by time</h3>
                <div className="flex items-center gap-3 text-[10px] text-neutral-500 dark:text-[#888888]">
                  <div className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-neutral-200 dark:bg-[#2e2e2e]"></span> 200&gt;</div>
                  <div className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-[#7a2e10]"></span> 500&gt;</div>
                  <div className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-[#c24a1a]"></span> 1,000&gt;</div>
                  <div className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-[#b91c1c]"></span> 2,000&gt;</div>
                </div>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "44px repeat(7, 36px)", gap: "2px", justifyContent: "start" }}>
                {/* Empty top-left cell */}
                <div></div>
                {/* Days Headers */}
                {days.map(d => (
                  <div key={d} className="text-center text-[11px] text-neutral-400 dark:text-[#666666] mb-2">{d}</div>
                ))}

                {/* Grid Rows */}
                {hours.map((h, hIndex) => (
                  <React.Fragment key={h}>
                    <div className="flex items-center text-[10px] text-neutral-400 dark:text-[#666666] justify-end pr-3 h-[36px]">{h}</div>
                    {days.map((_, dIndex) => (
                      <div 
                        key={`${dIndex}-${hIndex}`} 
                        className={`rounded-sm ${getHeatmapColor(dIndex, hIndex)} w-[36px] h-[36px]`}
                      />
                    ))}
                  </React.Fragment>
                ))}
              </div>
            </div>

            {/* AreaChart */}
            <div className="bg-white dark:bg-[#252525] border border-neutral-200 dark:border-[#333] rounded-xl p-4 shadow-sm flex flex-col flex-1">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-neutral-900 dark:text-white font-medium">Monthly Sales performance</h3>
                <div className="flex items-center gap-4 text-[11px] text-neutral-500 dark:text-[#888888]">
                  <div className="flex items-center gap-2"><span className="w-3 h-0.5 bg-[#b91c1c]"></span> Sales</div>
                  <div className="flex items-center gap-2"><span className="w-3 h-0.5 bg-[#ca8a04] border-t border-dashed border-[#ca8a04] bg-transparent"></span> Target</div>
                </div>
              </div>
              <div style={{ width: "100%", minWidth: 0 }}>
                <ResponsiveContainer width="100%" height={220}>
                                    <AreaChart data={chartData} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorSales" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#b91c1c" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#b91c1c" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorTarget" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#ca8a04" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#ca8a04" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={isDark ? "#333333" : "#e5e5e5"} />
                    <XAxis 
                      dataKey="name" 
                      axisLine={false} 
                      tickLine={false} 
                      tick={{ fill: isDark ? '#888888' : '#a3a3a3', fontSize: 11 }}
                      dy={10}
                    />
                    <YAxis 
                      axisLine={false} 
                      tickLine={false} 
                      tick={{ fill: isDark ? '#888888' : '#a3a3a3', fontSize: 11 }}
                      ticks={[0, 1500, 3000, 4500, 6000]}
                    />
                    <Tooltip content={<CustomTooltip />} cursor={{ stroke: isDark ? '#444' : '#ccc', strokeWidth: 1, strokeDasharray: "4 4" }} />
                    <Area type="monotone" dataKey="sales" stroke="#b91c1c" fillOpacity={1} fill="url(#colorSales)" strokeWidth={2} dot={false} activeDot={{ r: 4, fill: '#b91c1c', strokeWidth: 0 }} />
                    <Area type="monotone" dataKey="target" stroke="#ca8a04" fillOpacity={1} fill="url(#colorTarget)" strokeWidth={2} strokeDasharray="4 2" dot={false} activeDot={{ r: 4, fill: '#ca8a04', strokeWidth: 0 }} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

          </div>

          {/* Bottom Row */}
          <div style={{ display: "grid", gridTemplateColumns: "minmax(0, 1fr) minmax(0, 1.6fr)", gap: 12 }}>
            
            {/* Sales by Country */}
            <div className="bg-white dark:bg-[#252525] border border-neutral-200 dark:border-[#333] rounded-xl p-4 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-neutral-900 dark:text-white font-medium">Sales by Country</h3>
                <button className="text-red-700 dark:text-red-500 text-[13px] hover:underline">View All</button>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                {sales.length === 0 ? <div className="col-span-2 text-center text-sm text-neutral-500 py-4">No sales data yet</div> : sales.map((c: any, i: number) => (
                  <div key={i} className="flex flex-col gap-1 p-3 rounded-lg border border-neutral-100 dark:border-[#2e2e2e] bg-neutral-50 dark:bg-[#1e1e1e]/50 hover:bg-red-50 dark:hover:bg-red-900/20 transition-premium hover:shadow-[0_4px_20px_-4px_rgba(0,0,0,0.1)] dark:hover:shadow-[0_4px_20px_-4px_rgba(0,0,0,0.5)]">
                    <div className="flex items-center gap-2">
                      <img src={`https://flagcdn.com/w40/${c.country_code}.png`} srcSet={`https://flagcdn.com/w80/${c.country_code}.png 2x`} width="20" alt={c.name} className="rounded-sm opacity-90" />
                      <span className="text-sm text-neutral-900 dark:text-white font-medium truncate">{c.name}</span>
                    </div>
                    <div className="text-[11px] text-neutral-500 dark:text-[#555555] ml-7">
                      {c.sales_amount + " Products"} Products
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Top Product Sales (We replace with TableWithDialog logic, but compact) */}
            <div className="w-full">
                <TableWithDialog />
            </div>

          </div>
          
          {/* Spacing for scroll */}
          

          <ClientTokenManager />

          {/* Back to Portal Block */}
          <div className="mt-4">
            <Link href="/chats-new/" className="block bg-white dark:bg-[#1e1e1e] border border-neutral-200 dark:border-[#2a2a2a] rounded-[12px] p-8 text-center hover:bg-neutral-50 dark:hover:bg-[#252525] transition-colors shadow-sm group">
                <div className="mx-auto w-12 h-12 rounded-full bg-neutral-100 dark:bg-[#2a2a2a] flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <ArrowLeft className="w-6 h-6 text-neutral-500 dark:text-[#888] group-hover:text-[#e05a2b] transition-colors" />
                </div>
                <h3 className="text-lg font-medium text-neutral-900 dark:text-white mb-1">Return to Chats</h3>
                <p className="text-sm text-neutral-500 dark:text-[#888]">Open the admin conversation workspace</p>
            </Link>
          </div>
        </div>
    </AppShell>
  );
}
