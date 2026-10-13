"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { KeyRound } from "lucide-react";

export default function DevTokenPage() {
  const router = useRouter();
  const [error, setError] = useState("");

  const handleTokenSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");
    const token = new FormData(e.currentTarget).get("token") as string;
    
    if (!token) return;

    try {
      const res = await fetch('/api/activate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token })
      });
      if (res.ok) {
        const resData = await res.json().catch(() => ({}));
        const masterKey = resData.master_key || token;
        localStorage.setItem('firby_master_key', masterKey);
        localStorage.setItem('dev_master_key', masterKey);
        localStorage.setItem('firby_dev_mode', 'true');
        router.replace('/panel/');
      } else {
        setError("Token inválido");
      }
    } catch(err) {
      setError("Error de conexión");
    }
  };

  React.useEffect(() => {
    document.documentElement.classList.remove('dark');
  }, []);

  return (
    <div className="w-full min-h-screen flex items-center justify-center bg-[#fafafa] p-4 font-sans text-neutral-900">
      <Card className="w-full max-w-md mx-auto rounded-3xl border-neutral-200 bg-white text-neutral-900 shadow-xl shadow-black/5 overflow-hidden p-1 sm:p-2">
        <CardHeader className="text-center flex flex-col items-center gap-4 pb-6">
          <div className="space-y-1">
            <CardTitle className="text-2xl font-bold tracking-tight text-neutral-900">API Token Access</CardTitle>
            <CardDescription className="text-neutral-500">
              Autentícate usando tu API token de desarrollador.
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-600 text-sm text-center">
                  {error}
              </div>
          )}
          <form onSubmit={handleTokenSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="token" className="text-neutral-700">Access Token</Label>
              <div className="relative">
                <KeyRound className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-neutral-400" />
                <Input 
                  id="token" 
                  name="token" 
                  type="password" 
                  placeholder="dev_xxxxxxxx..." 
                  className="pl-9 bg-white border-neutral-200 text-neutral-900 placeholder:text-neutral-400 focus-visible:ring-neutral-400/20" 
                  required 
                />
              </div>
            </div>
            <Button
              type="submit"
              className="w-full bg-[#b8f901] border border-[#b8f901] text-[#09090b] hover:bg-[#a6e000] hover:border-[#a6e000] font-bold text-sm py-2.5 rounded-lg shadow-sm transition active:scale-[0.99]"
            >
              Autenticar Token
            </Button>
          </form>
        </CardContent>
        <CardFooter className="flex justify-center">
            <Button variant="link" className="text-sm text-neutral-500 hover:text-neutral-900" onClick={() => router.push('/dev-portal/login/')}>
                &larr; Volver al inicio de sesión
            </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
