"use client";
import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { AuthForm } from "@/components/ui/sign-in";

export default function CustomerSignInPage() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState("");

  useEffect(() => {
    document.documentElement.classList.remove('dark');
    try {
      const params = new URLSearchParams(window.location.search);
      const qEmail = params.get("email");
      if (qEmail) setEmail(qEmail);
    } catch (e) {}
  }, []);

  const handleEmailSubmit = async (data: { email: string; password?: string }) => {
    setError("");
    if (!data.password) {
      setError("Por favor ingresa tu contraseña.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: data.email, password: data.password })
      });
      
      if (!res.ok) {
        // Fallback: master key direct
        try {
          const configRes = await fetch('/api/activate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: data.password })
          });
          if (configRes.ok) {
            const configData = await configRes.json().catch(() => ({}));
            localStorage.setItem('firby_master_key', configData.master_key || data.password);
            localStorage.setItem('firby_user_email', data.email.trim().toLowerCase());
            localStorage.removeItem('dev_master_key');
            localStorage.removeItem('firby_dev_mode');
            router.replace('/workspace/');
            return;
          }
        } catch(err) {}
        setError("Credenciales incorrectas. Verifica tu correo y contraseña.");
        setLoading(false);
        return;
      }
      
      const resData = await res.json();
      if (resData.onboarding_done === 0 || resData.redirect === '/onboarding') {
        localStorage.removeItem('firby_master_key');
        localStorage.removeItem('firby_onboarding_done');
        localStorage.setItem('firby_user_email', data.email.trim().toLowerCase());
        localStorage.setItem('firby_auth_provider', 'email_password');
        router.replace('/onboarding');
        return;
      }
      if (resData.master_key) {
        localStorage.setItem('firby_master_key', resData.master_key);
        localStorage.setItem('firby_user_email', data.email.trim().toLowerCase());
        localStorage.setItem('firby_onboarding_done', 'true');
        localStorage.removeItem('dev_master_key');
        localStorage.removeItem('firby_dev_mode');
        router.replace('/workspace/');
      } else {
        setError("Credenciales incorrectas. Verifica tu correo y contraseña.");
        setLoading(false);
      }
    } catch (err) {
      setError("Error de conexión. Intenta nuevamente.");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#fafafa] flex flex-col justify-between items-center p-4 selection:bg-[#b8f901] selection:text-black">
      <div />
      <main className="w-full flex flex-col items-center justify-center py-6">

        <AuthForm
          title="Iniciar Sesión"
          description="Ingresa a tu espacio de trabajo para gestionar tu agente de IA y revisar tus conversaciones."
          emailLabel="Correo Electrónico"
          passwordLabel="Contraseña"
          submitLabel="Iniciar Sesión"
          initialEmail={email}
          isLoading={loading}
          onEmailSubmit={handleEmailSubmit}
          errorMsg={error}
          logo={null}
        />
      </main>

      <footer className="w-full py-6 text-center text-xs text-neutral-400 flex items-center justify-center gap-2">
        <a href="/terms" target="_blank" className="hover:text-neutral-700 underline transition">
          Condiciones de uso
        </a>
        <span className="text-neutral-300">·</span>
        <a href="/privacy" target="_blank" className="hover:text-neutral-700 underline transition">
          Política de privacidad
        </a>
      </footer>
    </div>
  );
}
