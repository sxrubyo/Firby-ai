"use client";

import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Mail, User, Lock, Building, Phone, KeyRound, ArrowRight, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";

export default function CreateAccountForm() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [businessName, setBusinessName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [token, setToken] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch("/api/auth/register-pro", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          business_name: businessName,
          email,
          phone,
          token,
          password,
          sector: "general",
          assistant_name: "Valentina",
          tone: "profesional"
        }),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        setError(data.detail || data.message || "Error al crear la cuenta");
        setLoading(false);
        return;
      }

      if (data.master_key) {
        localStorage.setItem("firby_master_key", data.master_key);
        localStorage.setItem("firby_user_email", email);
        localStorage.removeItem("dev_master_key");
        localStorage.removeItem("firby_dev_mode");
      }

      setSuccess(true);
      setTimeout(() => {
        router.replace(data.redirect || "/panel/");
      }, 1000);
    } catch (err) {
      setError("Error de conexión con el servidor");
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-[#0a0a0c] p-4 font-sans text-neutral-100">
      <div className="w-full max-w-md flex flex-col items-center">
        
        {/* Clean Logo */}
        <div className="mb-6 flex items-center justify-center">
          <img
            src="/isotype.png"
            alt="Firby"
            className="h-10 w-auto object-contain brightness-0 invert select-none"
          />
        </div>

        <Card className="w-full border-[#2a2a2a] bg-[#111111] text-neutral-100 shadow-2xl shadow-black/40">
          <CardHeader className="text-center pb-4">
            <CardTitle className="text-2xl font-semibold text-white tracking-tight">
              Crea tu Cuenta
            </CardTitle>
            <CardDescription className="text-sm text-neutral-400 mt-1">
              Ingresa tus datos y token de activación para configurar tu espacio de trabajo.
            </CardDescription>
          </CardHeader>
          
          <CardContent className="space-y-4">
            {error && (
              <div className="p-3 bg-red-950/50 border border-red-900 rounded-lg text-red-200 text-xs text-center font-medium">
                {error}
              </div>
            )}

            {success && (
              <div className="p-3 bg-emerald-950/50 border border-emerald-900 rounded-lg text-emerald-200 text-xs text-center font-medium">
                Cuenta activada con éxito. Redirigiendo...
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-3">
              <div>
                <Label htmlFor="name" className="text-xs text-neutral-300 font-medium">
                  Nombre Completo
                </Label>
                <div className="flex items-center gap-2 border border-[#333] rounded-lg px-3 py-2 bg-[#1a1a1a] mt-1 focus-within:border-neutral-500 transition">
                  <User className="w-4 h-4 text-neutral-500 shrink-0" />
                  <Input
                    id="name"
                    type="text"
                    placeholder="Santiago Rubio"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    className="border-0 bg-transparent text-white placeholder:text-neutral-600 focus-visible:ring-0 focus-visible:outline-none shadow-none h-auto p-0 text-sm"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="businessName" className="text-xs text-neutral-300 font-medium">
                  Nombre de la Empresa o Clínica
                </Label>
                <div className="flex items-center gap-2 border border-[#333] rounded-lg px-3 py-2 bg-[#1a1a1a] mt-1 focus-within:border-neutral-500 transition">
                  <Building className="w-4 h-4 text-neutral-500 shrink-0" />
                  <Input
                    id="businessName"
                    type="text"
                    placeholder="Clínica Dental Sonrisas"
                    value={businessName}
                    onChange={(e) => setBusinessName(e.target.value)}
                    required
                    className="border-0 bg-transparent text-white placeholder:text-neutral-600 focus-visible:ring-0 focus-visible:outline-none shadow-none h-auto p-0 text-sm"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="email" className="text-xs text-neutral-300 font-medium">
                  Correo Electrónico
                </Label>
                <div className="flex items-center gap-2 border border-[#333] rounded-lg px-3 py-2 bg-[#1a1a1a] mt-1 focus-within:border-neutral-500 transition">
                  <Mail className="w-4 h-4 text-neutral-500 shrink-0" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="contacto@empresa.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="border-0 bg-transparent text-white placeholder:text-neutral-600 focus-visible:ring-0 focus-visible:outline-none shadow-none h-auto p-0 text-sm"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="phone" className="text-xs text-neutral-300 font-medium">
                  WhatsApp / Teléfono
                </Label>
                <div className="flex items-center gap-2 border border-[#333] rounded-lg px-3 py-2 bg-[#1a1a1a] mt-1 focus-within:border-neutral-500 transition">
                  <Phone className="w-4 h-4 text-neutral-500 shrink-0" />
                  <Input
                    id="phone"
                    type="tel"
                    placeholder="+57 300 123 4567"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    required
                    className="border-0 bg-transparent text-white placeholder:text-neutral-600 focus-visible:ring-0 focus-visible:outline-none shadow-none h-auto p-0 text-sm"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="token" className="text-xs text-neutral-300 font-medium">
                  Token de Activación
                </Label>
                <div className="flex items-center gap-2 border border-[#333] rounded-lg px-3 py-2 bg-[#1a1a1a] mt-1 focus-within:border-neutral-500 transition">
                  <KeyRound className="w-4 h-4 text-neutral-500 shrink-0" />
                  <Input
                    id="token"
                    type="text"
                    placeholder="ACTV-XXXX-XXXX"
                    value={token}
                    onChange={(e) => setToken(e.target.value)}
                    required
                    className="border-0 bg-transparent text-white placeholder:text-neutral-600 focus-visible:ring-0 focus-visible:outline-none shadow-none h-auto p-0 text-sm uppercase font-mono"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="password" className="text-xs text-neutral-300 font-medium">
                  Contraseña
                </Label>
                <div className="flex items-center gap-2 border border-[#333] rounded-lg px-3 py-2 bg-[#1a1a1a] mt-1 focus-within:border-neutral-500 transition">
                  <Lock className="w-4 h-4 text-neutral-500 shrink-0" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    minLength={6}
                    className="border-0 bg-transparent text-white placeholder:text-neutral-600 focus-visible:ring-0 focus-visible:outline-none shadow-none h-auto p-0 text-sm"
                  />
                </div>
              </div>

              <Button
                type="submit"
                disabled={loading || success}
                className="w-full bg-white text-black hover:bg-neutral-200 font-medium text-sm py-2.5 rounded-lg shadow-sm transition mt-3 flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Activando cuenta...</span>
                  </>
                ) : (
                  <>
                    <span>Activar y Comenzar</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </Button>
            </form>

            <div className="pt-2 text-center">
              <p className="text-xs text-neutral-400">
                ¿Ya tienes una cuenta?{" "}
                <button
                  type="button"
                  onClick={() => router.push("/sign-in/")}
                  className="text-white font-medium hover:underline ml-1"
                >
                  Iniciar Sesión
                </button>
              </p>
            </div>

            <p className="text-[11px] text-neutral-600 text-center pt-2">
              Al continuar, aceptas nuestros{" "}
              <a href="#" className="underline hover:text-neutral-400">
                Términos de Servicio
              </a>{" "}
              y{" "}
              <a href="#" className="underline hover:text-neutral-400">
                Política de Privacidad
              </a>
              .
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
