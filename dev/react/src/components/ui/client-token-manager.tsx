"use client";

import React, { useEffect, useState } from "react";
import { RefreshCw, Copy, KeyRound, ShieldCheck, UserPlus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function ClientTokenManager() {
  const [clinicLabel, setClinicLabel] = useState("");
  const [tokenType, setTokenType] = useState<"business_owner" | "admin_pro">("business_owner");
  const [tokens, setTokens] = useState<any[]>([]);
  const [creating, setCreating] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [newToken, setNewToken] = useState("");
  const [expiresAt, setExpiresAt] = useState("");
  const [message, setMessage] = useState("");
  const [users, setUsers] = useState<any[]>([]);
  const [error, setError] = useState("");

  const getMasterKey = () => {
    if (typeof window === "undefined") return "";
    return localStorage.getItem("dev_master_key") || localStorage.getItem("firby_master_key") || "";
  };

  const loadTokens = async () => {
    setRefreshing(true);
    setError("");
    try {
      const master = getMasterKey();
      
      // Fetch users
      const usersRes = await fetch("/api/dev/users", {
        headers: { "X-Master-Key": master },
      });
      if (usersRes.ok) {
        const usersData = await usersRes.json();
        setUsers(usersData.users || []);
        if (usersData.users && usersData.users.length > 0 && !clinicLabel) {
            setClinicLabel(usersData.users[0].name);
        }
      }

      const res = await fetch("/api/tokens", {
        headers: { "X-Master-Key": master },
      });
      if (!res.ok) throw new Error("No se pudieron cargar los tokens");
      const data = await res.json();
      setTokens(Array.isArray(data.tokens) ? data.tokens : []);
    } catch (err: any) {
      setError(err?.message || "No se pudieron cargar los tokens");
    }
    setRefreshing(false);
  };

  useEffect(() => {
    loadTokens();
  }, []);

  const copyToken = async (token: string) => {
    try {
      await navigator.clipboard.writeText(token);
      setMessage("Token copiado al portapapeles");
      setTimeout(() => setMessage(""), 2500);
    } catch {
      setError("No se pudo copiar el token");
    }
  };

  const createToken = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");
    setMessage("");
    if (!clinicLabel.trim()) {
      setError("Escribe el nombre de la clínica o cliente");
      return;
    }

    setCreating(true);
    try {
      const master = getMasterKey();
      const res = await fetch("/api/tokens/create", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Master-Key": master,
        },
        body: JSON.stringify({
          clinic_label: clinicLabel.trim(),
          token_type: tokenType,
        }),
      });

      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.detail || "No se pudo crear el token");
      }

      setNewToken(data.token || "");
      setExpiresAt(data.expires_at || "");
      setMessage(data.instructions || "Token creado");
      setClinicLabel("");
      setTokenType("business_owner");
      await loadTokens();
    } catch (err: any) {
      setError(err?.message || "No se pudo crear el token");
    }
    setCreating(false);
  };

  return (
    <section className="mt-4">
      <div className="bg-white dark:bg-[#1e1e1e] border border-neutral-200 dark:border-[#2a2a2a] rounded-[12px] p-6 shadow-sm">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <div className="flex items-center gap-2 text-neutral-900 dark:text-white">
              <UserPlus className="w-5 h-5 text-[#e05a2b]" />
              <h3 className="text-lg font-medium">Client Access Tokens</h3>
            </div>
            <p className="text-sm text-neutral-500 dark:text-[#888] mt-1 max-w-2xl">
              Crea sesiones nuevas para clientes. El token se canjea directo desde <span className="font-medium text-neutral-700 dark:text-neutral-200">/sign-in</span> con <span className="font-medium text-neutral-700 dark:text-neutral-200">O ingresa con Api Token</span>.
            </p>
          </div>
          <button onClick={loadTokens} className="p-2 bg-neutral-50 dark:bg-[#252525] border border-neutral-200 dark:border-[#333] rounded-md hover:bg-neutral-100 dark:hover:bg-[#2e2e2e] transition-colors self-start">
            <RefreshCw className={`w-5 h-5 text-neutral-600 dark:text-neutral-300 ${refreshing ? "animate-spin" : ""}`} />
          </button>
        </div>

        <form onSubmit={createToken} className="mt-6 grid grid-cols-1 md:grid-cols-[1.4fr,1fr,auto] gap-3 items-end">
          <div className="space-y-2">
            <Label htmlFor="clinic-label" className="text-sm text-neutral-700 dark:text-neutral-300">Cliente / Clínica</Label>
            {users.length > 0 ? (
                <select
                  id="clinic-label"
                  value={clinicLabel}
                  onChange={(e) => setClinicLabel(e.target.value)}
                  className="h-10 w-full rounded-md border border-neutral-200 dark:border-[#333] bg-neutral-50 dark:bg-[#252525] px-3 text-sm text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#e05a2b]"
                >
                  {users.map((u, i) => (
                      <option key={i} value={u.name}>{u.name} ({u.email || u.status})</option>
                  ))}
                </select>
            ) : (
                <Input
                  id="clinic-label"
                  value={clinicLabel}
                  onChange={(e) => setClinicLabel(e.target.value)}
                  placeholder="Nombre del cliente o clínica"
                  className="bg-neutral-50 dark:bg-[#252525] border-neutral-200 dark:border-[#333] text-neutral-900 dark:text-white"
                />
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="token-type" className="text-sm text-neutral-700 dark:text-neutral-300">Tipo de acceso</Label>
            <select
              id="token-type"
              value={tokenType}
              onChange={(e) => setTokenType(e.target.value as "business_owner" | "admin_pro")}
              className="h-10 w-full rounded-md border border-neutral-200 dark:border-[#333] bg-neutral-50 dark:bg-[#252525] px-3 text-sm text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#e05a2b]"
            >
              <option value="business_owner">Cliente</option>
              <option value="admin_pro">Admin Pro</option>
            </select>
          </div>

          <Button type="submit" disabled={creating} className="h-10 bg-[#e05a2b] text-white hover:bg-[#c94e24]">
            <KeyRound className="mr-2 h-4 w-4" />
            {creating ? "Generando..." : "Generar token"}
          </Button>
        </form>

        {error && (
          <div className="mt-4 p-3 rounded-md border border-red-500/20 bg-red-500/10 text-red-600 dark:text-red-400 text-sm">
            {error}
          </div>
        )}

        {message && (
          <div className="mt-4 p-3 rounded-md border border-emerald-500/20 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-sm">
            {message}
          </div>
        )}

        {newToken && (
          <div className="mt-5 p-4 rounded-xl border border-neutral-200 dark:border-[#333] bg-neutral-50 dark:bg-[#252525]">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
              <div>
                <p className="text-xs uppercase tracking-[0.08em] text-neutral-500 dark:text-[#888] mb-1">Token generado</p>
                <p className="font-mono text-sm text-neutral-900 dark:text-white break-all">{newToken}</p>
                {expiresAt && <p className="text-xs text-neutral-500 dark:text-[#888] mt-1">Expira: {expiresAt}</p>}
              </div>
              <Button type="button" variant="outline" onClick={() => copyToken(newToken)} className="border-neutral-200 dark:border-[#333] bg-white dark:bg-[#1e1e1e]">
                <Copy className="mr-2 h-4 w-4" /> Copiar token
              </Button>
            </div>
          </div>
        )}

        <div className="mt-6 space-y-2">
          <div className="flex items-center gap-2 text-sm font-medium text-neutral-800 dark:text-neutral-200">
            <ShieldCheck className="w-4 h-4 text-[#e05a2b]" />
            Tokens recientes
          </div>
          {tokens.length === 0 ? (
            <p className="text-sm text-neutral-500 dark:text-[#888]">No hay tokens activos aún.</p>
          ) : (
            <div className="grid gap-2">
              {tokens.slice(0, 5).map((token) => (
                <div key={token.token} className="flex flex-col gap-1 rounded-lg border border-neutral-200 dark:border-[#2f2f2f] bg-white dark:bg-[#1b1b1b] px-3 py-2">
                  <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-1">
                    <div>
                      <p className="text-sm font-medium text-neutral-900 dark:text-white">{token.clinic_label}</p>
                      <p className="text-xs text-neutral-500 dark:text-[#888]">{token.is_active ? "Activo" : "Inactivo"} · {token.token_type || "business_owner"}</p>
                    </div>
                    <button type="button" onClick={() => copyToken(token.token)} className="text-xs font-medium text-[#e05a2b] hover:underline self-start md:self-center">Copiar</button>
                  </div>
                  <p className="font-mono text-[11px] text-neutral-500 dark:text-[#777] break-all">{token.token}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
